"""Error fixing node - analyzes errors and prepares for retry.

This node:
1. Analyzes execution/validation failures
2. Uses LLM to diagnose root cause
3. Provides suggestions for fixing
4. Increments iteration counter
5. Routes back to code generation (if under max iterations)
"""
from app.agents.state import AgentState, StepType
from app.services.llm.factory import LLMFactory
from app.services.llm.output_schema import ErrorAnalysisOutput
from app.services.llm.output_parser import OutputParser


async def error_fixing_node(state: AgentState) -> AgentState:
    """Error fixing node - analyze errors and prepare for retry.

    Args:
        state: Current agent state

    Returns:
        Updated state with error analysis
    """
    print(f"\n{'='*60}")
    print(f"ERROR FIXING NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    # Check if we've hit max iterations
    if state["iteration"] >= state["max_iterations"]:
        print(
            f"\n❌ Maximum iterations ({state['max_iterations']}) reached - stopping"
        )
        state["is_complete"] = True
        state["completion_reason"] = (
            f"max_iterations_reached ({state['max_iterations']})"
        )
        return state

    # Get LLM service
    llm = LLMFactory.create(state["llm_provider"])

    # Build error context
    error_context = []

    # Add execution errors if present
    if state["execution_results"]:
        last_exec = state["execution_results"][-1]
        if not last_exec.success:
            error_context.append("**Execution Error:**")
            if last_exec.timed_out:
                error_context.append(
                    f"- Code timed out after {last_exec.execution_time:.1f}s"
                )
                error_context.append(
                    "- This usually means infinite loop or very inefficient algorithm"
                )
            else:
                error_context.append(f"- Exit code: {last_exec.exit_code}")
                error_context.append(f"- Error: {last_exec.error}")

    # Add validation errors
    if state["failed_tests"] > 0:
        error_context.append(
            f"\n**Validation Errors:** {state['failed_tests']}/{len(state['test_cases'])} tests failed"
        )
        for i, result in enumerate(state["validation_results"], 1):
            if not result.passed:
                error_context.append(f"\nFailed Test {i}: {result.test_case.description}")
                error_context.append(f"  Inputs: {result.test_case.inputs}")
                error_context.append(
                    f"  Expected: {result.test_case.expected_output}"
                )
                if result.actual_output:
                    error_context.append(f"  Actual: {result.actual_output}")
                if result.error:
                    error_context.append(f"  Error: {result.error}")

    error_summary = "\n".join(error_context)

    print(f"\n📋 Error context:")
    print(error_summary[:500])
    if len(error_summary) > 500:
        print(f"... ({len(error_summary) - 500} more characters)")

    # Construct error analysis prompt
    system_message = (
        "You are an expert Python debugger. "
        "Analyze code errors and provide clear, actionable fixes."
    )

    user_message = f"""Analyze this code failure and suggest fixes:

**User Query:** {state['user_query']}

**Current Code:**
```python
{state['current_code']}
```

**Error Information:**
{error_summary}

**Previous Approach:** {state['approach']}

Analyze:
1. **Root Cause**: What exactly is wrong with the code?
2. **Failed Test Details**: For each failed test, explain why it failed
3. **Suggested Fix**: Concrete changes needed to fix the code

Return in JSON format matching ErrorAnalysisOutput schema.
"""

    # Call LLM with structured output (Directive 03)
    try:
        analysis_output, token_usage = await llm.generate_structured(
            prompt=user_message,
            schema=ErrorAnalysisOutput,
            system_message=system_message,
        )

        # Validate output (Directive 03 - reject if malformed)
        validated_output = OutputParser.parse_structured_output(
            analysis_output.model_dump_json(), ErrorAnalysisOutput
        )

        # Update state
        state["last_error_analysis"] = (
            f"Root Cause: {validated_output.root_cause}\n\n"
            f"Suggested Fix: {validated_output.suggested_fix}"
        )
        state["error_history"].append(state["last_error_analysis"])
        state["current_step"] = StepType.ERROR_FIXING

        # Increment iteration for next attempt
        state["iteration"] += 1

        # Track tokens (Directive 09)
        step_key = f"error_fixing_iter_{state['iteration'] - 1}"
        state["token_usage"][step_key] = {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens,
            "cost_usd": token_usage.cost_usd,
        }
        state["total_tokens"] += token_usage.total_tokens
        state["estimated_cost_usd"] += token_usage.cost_usd

        print(f"\n✅ Error analysis complete:")
        print(f"   Root cause: {validated_output.root_cause[:100]}...")
        print(f"   Suggested fix: {validated_output.suggested_fix[:100]}...")
        print(
            f"   Tokens: {token_usage.total_tokens} (${token_usage.cost_usd:.4f})"
        )
        print(f"\n🔄 Retrying with iteration {state['iteration']}...")

    except Exception as e:
        print(f"\n❌ Error analysis failed: {type(e).__name__}: {str(e)}")
        state["is_complete"] = True
        state["completion_reason"] = f"Error analysis failed: {str(e)}"

    return state
