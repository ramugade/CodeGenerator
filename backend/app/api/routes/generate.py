"""POST /api/generate endpoint with Server-Sent Events streaming."""
import uuid
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import GenerateRequest
from app.agents.state import create_initial_state
from app.agents.graph import code_generation_graph
from app.utils.streaming import stream_agent_events, create_error_event

router = APIRouter()


async def generate_code_stream(request: GenerateRequest) -> AsyncGenerator[str, None]:
    """Generate code with streaming events.

    This is the core SSE stream generator that:
    1. Creates initial agent state
    2. Streams the LangGraph workflow
    3. Emits events after each node execution
    4. Handles errors gracefully

    Args:
        request: Generate request with query and configuration

    Yields:
        SSE formatted event strings
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create initial state
        initial_state = create_initial_state(
            user_query=request.query,
            session_id=session_id,
            llm_provider=request.llm_provider,
            user_provided_tests=request.user_provided_tests,
            max_iterations=request.max_iterations,
        )

        # Stream workflow execution
        # LangGraph's astream() yields state after each node
        async for state in code_generation_graph.astream(initial_state):
            # state is a dict with node name as key
            # Get the actual state from the dict
            if isinstance(state, dict):
                # Extract the state value (node output)
                actual_state = list(state.values())[0] if state else initial_state
            else:
                actual_state = state

            # Stream events based on current step
            async for event in stream_agent_events(actual_state):
                yield event

            # Check if workflow is complete
            if actual_state.get("is_complete"):
                break

    except Exception as e:
        # Stream error event
        error_msg = f"{type(e).__name__}: {str(e)}"
        yield create_error_event(error_msg)


@router.post("/generate")
async def generate_code(request: GenerateRequest):
    """Generate Python code from natural language description with SSE streaming.

    This endpoint:
    1. Accepts a coding task description
    2. Streams real-time updates via Server-Sent Events (SSE)
    3. Returns working Python code with test validation

    Event types emitted:
    - planning: Problem understanding and approach
    - test_inference: Generated test cases (or test_inference_skipped)
    - code_generated: Generated code (versioned)
    - execution: Code execution results
    - validation: Test validation results
    - error_fixing: Error analysis (if retrying)
    - complete: Final results
    - error: Error occurred

    Args:
        request: GenerateRequest with query and configuration

    Returns:
        StreamingResponse with Server-Sent Events
    """
    # Validate request
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Return SSE stream
    return StreamingResponse(
        generate_code_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
