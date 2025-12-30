"""Planning node - analyzes user query and creates execution plan.

This is the first node in the LangGraph workflow. It:
1. Uses LLM to understand the problem
2. Creates a high-level approach
3. Updates state with planning results
4. Emits SSE event for frontend
"""
from app.agents.state import AgentState, StepType
from app.services.llm.factory import LLMFactory
from app.services.llm.output_schema import PlanningOutput
from app.services.llm.output_parser import OutputParser


async def planning_node(state: AgentState) -> AgentState:
    """Planning node - analyze user query and create execution plan.

    Args:
        state: Current agent state

    Returns:
        Updated state with planning results
    """
    print(f"\n{'='*60}")
    print(f"PLANNING NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    # Get LLM service
    llm = LLMFactory.create(state["llm_provider"])

    # Construct planning prompt
    system_message = (
        "You are an expert Python programmer and problem solver. "
        "Analyze the user's request and create a clear execution plan."
    )

    user_message = f"""Analyze this programming task:

**User Query:** {state['user_query']}

Provide:
1. **Problem Understanding**: What exactly does the user want? Include:
   - Input format and types
   - Expected output format
   - Any constraints or requirements
   - Edge cases to consider

2. **Approach**: How will you solve this? Include:
   - Algorithm or method to use
   - Key implementation steps
   - Time/space complexity if relevant
   - Libraries or techniques needed

Return your analysis in JSON format matching the PlanningOutput schema.
"""

    # Call LLM with structured output (Directive 03)
    try:
        planning_output, token_usage = await llm.generate_structured(
            prompt=user_message,
            schema=PlanningOutput,
            system_message=system_message,
        )

        # Validate output (Directive 03 - reject if malformed)
        validated_output = OutputParser.parse_structured_output(
            planning_output.model_dump_json(), PlanningOutput
        )

        # Update state
        state["problem_understanding"] = validated_output.problem_understanding
        state["approach"] = validated_output.approach
        state["current_step"] = StepType.PLANNING

        # Track tokens (Directive 09)
        state["token_usage"]["planning"] = {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens,
            "cost_usd": token_usage.cost_usd,
        }
        state["total_tokens"] += token_usage.total_tokens
        state["estimated_cost_usd"] += token_usage.cost_usd

        print(f"\n✅ Planning complete:")
        print(f"   Understanding: {validated_output.problem_understanding[:100]}...")
        print(f"   Approach: {validated_output.approach[:100]}...")
        print(
            f"   Tokens: {token_usage.total_tokens} (${token_usage.cost_usd:.4f})"
        )

    except Exception as e:
        print(f"\n❌ Planning failed: {type(e).__name__}: {str(e)}")
        state["is_complete"] = True
        state["completion_reason"] = f"Planning failed: {str(e)}"

    return state
