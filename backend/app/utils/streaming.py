"""Server-Sent Events (SSE) utilities for streaming agent events to frontend.

SSE Format:
event: {event_type}
data: {json_payload}

"""
import json
from typing import Any, AsyncGenerator
from app.agents.state import AgentState, StepType


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event.

    Args:
        event_type: Type of event (planning, code_generated, etc.)
        data: Event data as dict

    Returns:
        Formatted SSE string
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"


async def stream_agent_events(
    state: AgentState,
) -> AsyncGenerator[str, None]:
    """Stream agent state updates as SSE events.

    This is called after each node execution to emit progress updates.

    Args:
        state: Current agent state

    Yields:
        SSE formatted event strings
    """
    current_step = state.get("current_step")

    # Planning event
    if current_step == StepType.PLANNING:
        if state.get("problem_understanding") and state.get("approach"):
            yield format_sse_event(
                "planning",
                {
                    "understanding": state["problem_understanding"],
                    "approach": state["approach"],
                },
            )

    # Optional test inference event (Directive 17)
    elif current_step == StepType.OPTIONAL_TEST_INFERENCE:
        if state.get("test_inference_skipped"):
            yield format_sse_event(
                "test_inference_skipped",
                {
                    "message": "Using user-provided test cases",
                    "test_count": len(state.get("test_cases", [])),
                },
            )
        elif state.get("test_cases"):
            yield format_sse_event(
                "test_inference",
                {
                    "test_cases": [
                        {
                            "description": tc.description,
                            "inputs": tc.inputs,
                            "expected_output": tc.expected_output,
                        }
                        for tc in state["test_cases"]
                    ],
                    "count": len(state["test_cases"]),
                },
            )

    # Code generation event
    elif current_step == StepType.CODE_GENERATION:
        if state.get("current_code"):
            code_version = len(state.get("code_history", []))
            yield format_sse_event(
                "code_generated",
                {
                    "code": state["current_code"],
                    "version": code_version,
                    "iteration": state.get("iteration", 1),
                },
            )

    # Execution event
    elif current_step == StepType.EXECUTION:
        if state.get("execution_results"):
            last_exec = state["execution_results"][-1]
            yield format_sse_event(
                "execution",
                {
                    "success": last_exec.success,
                    "output": last_exec.output,
                    "error": last_exec.error,
                    "execution_time": last_exec.execution_time,
                    "timed_out": last_exec.timed_out,
                },
            )

    # Validation event
    elif current_step == StepType.VALIDATION:
        yield format_sse_event(
            "validation",
            {
                "passed": state.get("passed_tests", 0),
                "failed": state.get("failed_tests", 0),
                "total": len(state.get("test_cases", [])),
                "results": [
                    {
                        "description": vr.test_case.description,
                        "passed": vr.passed,
                        "actual_output": vr.actual_output,
                        "expected_output": vr.test_case.expected_output,
                        "error": vr.error,
                    }
                    for vr in state.get("validation_results", [])
                ],
            },
        )

    # Error fixing event
    elif current_step == StepType.ERROR_FIXING:
        if state.get("last_error_analysis"):
            yield format_sse_event(
                "error_fixing",
                {
                    "analysis": state["last_error_analysis"],
                    "iteration": state.get("iteration", 1),
                },
            )

    # Completion event
    if state.get("is_complete"):
        yield format_sse_event(
            "complete",
            {
                "success": state.get("completion_reason") == "success",
                "reason": state.get("completion_reason"),
                "final_code": state.get("current_code"),
                "final_output": state.get("final_output"),
                "iterations": state.get("iteration", 1),
                "passed_tests": state.get("passed_tests", 0),
                "total_tests": len(state.get("test_cases", [])),
                "token_usage": {
                    "total_tokens": state.get("total_tokens", 0),
                    "estimated_cost_usd": state.get("estimated_cost_usd", 0.0),
                    "breakdown": state.get("token_usage", {}),
                },
            },
        )


def create_error_event(error_message: str) -> str:
    """Create an error SSE event.

    Args:
        error_message: Error message

    Returns:
        Formatted SSE error event
    """
    return format_sse_event(
        "error",
        {
            "error": error_message,
        },
    )
