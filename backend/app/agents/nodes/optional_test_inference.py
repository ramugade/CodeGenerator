"""Optional test inference node (Directive 17).

This node is SKIPPED if user provides test cases.
If no tests provided, LLM infers comprehensive test cases from the query.
"""
from app.agents.state import AgentState, StepType, TestCase
from app.services.llm.factory import LLMFactory
from app.services.llm.output_parser import OutputParser
from pydantic import BaseModel, Field


class TestInferenceOutputSchema(BaseModel):
    """Structured output for test case inference (Directive 03)."""

    test_cases: list[TestCase] = Field(
        description=(
            "List of comprehensive test cases covering: "
            "basic functionality, edge cases, boundary conditions."
        ),
        min_length=1,
    )
    reasoning: str = Field(
        description="Brief explanation of why these test cases were chosen"
    )


async def optional_test_inference_node(state: AgentState) -> AgentState:
    """Optional test inference - infer test cases if not user-provided.

    DIRECTIVE 17: This node is SKIPPED if state['test_inference_skipped'] is True.

    Args:
        state: Current agent state

    Returns:
        Updated state with test cases
    """
    print(f"\n{'='*60}")
    print(f"OPTIONAL TEST INFERENCE NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    # Check if user provided tests (Directive 17)
    if state["test_inference_skipped"]:
        print(
            f"\n⏭️  Skipping test inference - user provided {len(state['test_cases'])} test(s)"
        )
        state["current_step"] = StepType.OPTIONAL_TEST_INFERENCE
        return state

    # No user-provided tests - infer with LLM
    print("\n🧪 Inferring test cases from query...")

    # Get LLM service
    llm = LLMFactory.create(state["llm_provider"])

    # Construct test inference prompt
    system_message = (
        "You are an expert at creating comprehensive test cases for code. "
        "Generate test cases that cover basic functionality, edge cases, and boundary conditions."
    )

    user_message = f"""Generate comprehensive test cases for this programming task:

**User Query:** {state['user_query']}

**Problem Understanding:** {state['problem_understanding']}

**Approach:** {state['approach']}

Create test cases that cover:
1. **Basic functionality**: Normal inputs and expected outputs
2. **Edge cases**: Empty inputs, single elements, special values
3. **Boundary conditions**: Maximum/minimum values, type boundaries

Each test case should have:
- `description`: What the test checks
- `inputs`: Input parameters as a dict (e.g., {{"numbers": [10, 20, 30]}})
- `expected_output`: The expected return value

Generate 3-5 diverse test cases.

Return in JSON format matching TestInferenceOutput schema.
"""

    # Call LLM with structured output (Directive 03)
    try:
        test_output, token_usage = await llm.generate_structured(
            prompt=user_message,
            schema=TestInferenceOutputSchema,
            system_message=system_message,
        )

        # Validate output (Directive 03 - reject if malformed)
        validated_output = OutputParser.parse_structured_output(
            test_output.model_dump_json(), TestInferenceOutputSchema
        )

        # Update state with inferred test cases
        state["test_cases"] = validated_output.test_cases
        state["current_step"] = StepType.OPTIONAL_TEST_INFERENCE

        # Track tokens (Directive 09)
        state["token_usage"]["optional_test_inference"] = {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens,
            "cost_usd": token_usage.cost_usd,
        }
        state["total_tokens"] += token_usage.total_tokens
        state["estimated_cost_usd"] += token_usage.cost_usd

        print(f"\n✅ Test inference complete:")
        print(f"   Generated {len(validated_output.test_cases)} test cases")
        print(f"   Reasoning: {validated_output.reasoning[:100]}...")
        print(
            f"   Tokens: {token_usage.total_tokens} (${token_usage.cost_usd:.4f})"
        )

        # Print test cases
        for i, test in enumerate(validated_output.test_cases, 1):
            print(f"\n   Test {i}: {test.description}")
            print(f"      Inputs: {test.inputs}")
            print(f"      Expected: {test.expected_output}")

    except Exception as e:
        print(f"\n❌ Test inference failed: {type(e).__name__}: {str(e)}")
        state["is_complete"] = True
        state["completion_reason"] = f"Test inference failed: {str(e)}"

    return state
