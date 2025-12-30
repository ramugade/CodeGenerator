"""Execution node - runs generated code in subprocess sandbox.

This node:
1. Executes code using SubprocessSandbox (Directive 06)
2. Captures output, errors, and timing
3. Stores execution result in state
"""
from app.agents.state import AgentState, StepType, ExecutionResult
from app.services.execution.sandbox import SubprocessSandbox


async def execution_node(state: AgentState) -> AgentState:
    """Execution node - execute code in subprocess sandbox.

    Args:
        state: Current agent state

    Returns:
        Updated state with execution results
    """
    print(f"\n{'='*60}")
    print(f"EXECUTION NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    if not state["current_code"]:
        print("\n❌ No code to execute!")
        state["is_complete"] = True
        state["completion_reason"] = "No code generated"
        return state

    # Create sandbox
    sandbox = SubprocessSandbox()

    print("\n⏳ Executing code in subprocess sandbox...")
    print(f"   Timeout: {sandbox.timeout}s")
    print(f"   Isolation: OS-level process isolation")

    try:
        # Execute code (Directive 06 - subprocess isolation)
        result = await sandbox.execute_code(state["current_code"])

        # Create execution result
        version_number = len(state["code_history"])
        exec_result = ExecutionResult(
            version=version_number,
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            timed_out=result.timed_out,
        )

        # Update state
        state["execution_results"].append(exec_result)
        state["current_step"] = StepType.EXECUTION

        # Print results
        if result.success:
            print(f"\n✅ Execution successful!")
            print(f"   Time: {result.execution_time:.3f}s")
            if result.output:
                output_preview = result.output.strip()[:200]
                print(f"   Output: {output_preview}")
                if len(result.output.strip()) > 200:
                    print(f"   ... ({len(result.output) - 200} more characters)")
        elif result.timed_out:
            print(f"\n⏰ Execution timed out!")
            print(f"   Time: {result.execution_time:.1f}s")
            print(f"   Error: {result.error}")
        else:
            print(f"\n❌ Execution failed!")
            print(f"   Time: {result.execution_time:.3f}s")
            print(f"   Exit code: {result.exit_code}")
            if result.error:
                error_preview = result.error.strip()[:300]
                print(f"   Error: {error_preview}")
                if len(result.error.strip()) > 300:
                    print(f"   ... ({len(result.error) - 300} more characters)")

    except Exception as e:
        print(f"\n❌ Execution error: {type(e).__name__}: {str(e)}")

        # Create failed execution result
        version_number = len(state["code_history"])
        exec_result = ExecutionResult(
            version=version_number,
            success=False,
            output="",
            error=f"Execution error: {type(e).__name__}: {str(e)}",
            execution_time=0.0,
            timed_out=False,
        )

        state["execution_results"].append(exec_result)
        state["current_step"] = StepType.EXECUTION

    return state
