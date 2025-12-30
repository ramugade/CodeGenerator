"""Code generation node - generates Python code using LLM.

This node:
1. Uses planning and test cases to generate code
2. Includes error context if iteration > 1
3. Validates code structure (no markdown wrappers)
4. Versions and stores code in history
"""
from app.agents.state import AgentState, StepType, CodeVersion
from app.services.llm.factory import LLMFactory
from app.services.llm.output_schema import CodeOutput
from app.services.llm.output_parser import OutputParser
from app.services.execution.validators import CodeValidator


async def code_generation_node(state: AgentState) -> AgentState:
    """Code generation node - generate Python code with LLM.

    Args:
        state: Current agent state

    Returns:
        Updated state with generated code
    """
    print(f"\n{'='*60}")
    print(f"CODE GENERATION NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    # Get LLM service
    llm = LLMFactory.create(state["llm_provider"])

    # Construct code generation prompt
    system_message = (
        "You are an expert Python programmer. "
        "Write clean, efficient, well-documented Python code. "
        "IMPORTANT: Return ONLY raw Python code in the 'code' field - NO markdown formatting, NO code fences."
    )

    # Build user prompt with context
    user_message = f"""Generate Python code for this task:

**User Query:** {state['user_query']}

**Problem Understanding:** {state['problem_understanding']}

**Approach:** {state['approach']}

**Test Cases to Satisfy:**
"""

    # Add test cases
    for i, test in enumerate(state["test_cases"], 1):
        user_message += f"\nTest {i}: {test.description}\n"
        user_message += f"  Inputs: {test.inputs}\n"
        user_message += f"  Expected Output: {test.expected_output}\n"

    # Add error context if this is a retry (iteration > 1)
    if state["iteration"] > 1 and state["last_error_analysis"]:
        user_message += f"\n\n**PREVIOUS ATTEMPT FAILED:**\n"
        user_message += f"Error Analysis: {state['last_error_analysis']}\n\n"
        user_message += "Please fix the issues and generate corrected code.\n"

    user_message += """

**Requirements:**
1. Include a main() function that accepts inputs as parameters
2. Return the result (don't just print it)
3. Handle all edge cases from test cases
4. Use proper error handling where appropriate
5. Clean, readable code with docstrings
6. NO imports from dangerous modules (os, subprocess, sys, socket, etc.)

**CRITICAL:** In the 'code' field, return ONLY the raw Python code.
DO NOT wrap it in markdown code fences (```python).
DO NOT include any markdown formatting.
Just the pure Python code as plain text.

Return in JSON format matching CodeOutput schema.
"""

    # Call LLM with structured output (Directive 03)
    try:
        code_output, token_usage = await llm.generate_structured(
            prompt=user_message,
            schema=CodeOutput,
            system_message=system_message,
        )

        # Validate output (Directive 03 - reject if malformed or has markdown)
        validated_output = OutputParser.parse_code_output(
            code_output.model_dump_json()
        )

        # Additional validation: syntax check
        syntax_validation = CodeValidator.validate_syntax(validated_output.code)
        if not syntax_validation.is_valid:
            print(f"\n❌ Syntax validation failed:")
            for issue in syntax_validation.issues:
                print(f"   - {issue}")
            raise ValueError(
                f"Generated code has syntax errors: {', '.join(syntax_validation.issues)}"
            )

        # Additional validation: dangerous imports
        import_validation = CodeValidator.detect_dangerous_imports(
            validated_output.code
        )
        if not import_validation.is_valid:
            print(f"\n❌ Dangerous imports detected:")
            for issue in import_validation.issues:
                print(f"   - {issue}")
            raise ValueError(
                f"Generated code contains dangerous imports: {', '.join(import_validation.issues)}"
            )

        # Anti-hardcoding check (Directive 05) - warn only, don't reject
        hardcoding_check = CodeValidator.detect_hardcoding(validated_output.code)
        if hardcoding_check.suspicious_patterns:
            print(f"\n⚠️  Anti-hardcoding warning (Directive 05):")
            for pattern in hardcoding_check.suspicious_patterns:
                print(f"   - {pattern}")

        # Create code version
        version_number = len(state["code_history"]) + 1
        code_version = CodeVersion(
            version=version_number,
            code=validated_output.code,
            iteration=state["iteration"],
        )

        # Update state
        state["code_history"].append(code_version)
        state["current_code"] = validated_output.code
        state["current_step"] = StepType.CODE_GENERATION

        # Track tokens (Directive 09)
        step_key = f"code_generation_iter_{state['iteration']}"
        state["token_usage"][step_key] = {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens,
            "cost_usd": token_usage.cost_usd,
        }
        state["total_tokens"] += token_usage.total_tokens
        state["estimated_cost_usd"] += token_usage.cost_usd

        print(f"\n✅ Code generation complete:")
        print(f"   Version: {version_number}")
        print(f"   Filename: {validated_output.filename}")
        print(f"   Lines of code: {len(validated_output.code.splitlines())}")
        print(f"   Explanation: {validated_output.explanation[:100]}...")
        print(
            f"   Tokens: {token_usage.total_tokens} (${token_usage.cost_usd:.4f})"
        )

        # Show code preview
        code_lines = validated_output.code.splitlines()
        preview_lines = code_lines[:10]
        print(f"\n   Code preview:")
        for line in preview_lines:
            print(f"   │ {line}")
        if len(code_lines) > 10:
            print(f"   │ ... ({len(code_lines) - 10} more lines)")

    except Exception as e:
        print(f"\n❌ Code generation failed: {type(e).__name__}: {str(e)}")
        state["is_complete"] = True
        state["completion_reason"] = f"Code generation failed: {str(e)}"

    return state
