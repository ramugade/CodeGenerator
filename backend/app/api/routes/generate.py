"""POST /api/generate endpoint with Server-Sent Events streaming."""
import asyncio
from typing import AsyncGenerator
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import GenerateRequest
from app.agents.state import create_initial_state
from app.agents.graph import code_generation_graph
from app.utils.streaming import stream_agent_events, create_error_event, format_sse_event
from app.db.base import get_db
from app.services.session_service import SessionService

router = APIRouter()


async def generate_code_stream(request: GenerateRequest, db: AsyncSession) -> AsyncGenerator[str, None]:
    """Generate code with streaming events and database persistence.

    This is the core SSE stream generator that:
    1. Creates or resumes session
    2. Streams the LangGraph workflow
    3. Persists messages and token usage to database
    4. Emits events after each node execution

    Args:
        request: Generate request with query and configuration
        db: Database session

    Yields:
        SSE formatted event strings
    """
    try:
        # 1. Create or resume session
        session_created = False
        if request.session_id:
            session = await SessionService.get_session(db, request.session_id)
            if not session:
                raise HTTPException(404, "Session not found")
            session_id = request.session_id
        else:
            title = request.query[:50] + ("..." if len(request.query) > 50 else "")
            session = await SessionService.create_session(db, title, request.llm_provider)
            session_id = session.id
            session_created = True

        # 2. Emit session_created event if new session
        if session_created:
            yield format_sse_event("session_created", {
                "session_id": session_id,
                "title": session.title,
                "llm_provider": session.llm_provider,
                "created_at": session.created_at.isoformat()
            })

        # Create initial state
        initial_state = create_initial_state(
            user_query=request.query,
            session_id=session_id,
            llm_provider=request.llm_provider,
            user_provided_tests=request.user_provided_tests,
            max_iterations=request.max_iterations,
        )

        # 3. Persist user query as the first message in this run
        message_order = await SessionService.get_next_message_order(db, session_id)
        await SessionService.save_message(
            db,
            session_id,
            "user_query",
            {"query": request.query, "timestamp": datetime.utcnow().isoformat()},
            message_order,
        )
        message_order += 1

        # 4. Run LangGraph workflow

        async for state in code_generation_graph.astream(initial_state):
            # Get the actual state from the dict
            actual_state = list(state.values())[0] if state else initial_state

            async for event_type, event_data in stream_agent_events(actual_state):
                # Persist message
                await SessionService.save_message(
                    db, session_id, event_type, event_data, message_order
                )
                message_order += 1

                # Persist token usage with model/provider
                if event_type in ["planning", "code_generated", "error_fixing"]:
                    step_key = f"{event_type}_iter_{actual_state['iteration']}"
                    if step_key in actual_state.get("token_usage", {}):
                        token_data = actual_state["token_usage"][step_key].copy()
                        # Add provider from request
                        token_data["provider"] = request.llm_provider
                        await SessionService.save_token_usage(db, session_id, step_key, token_data)

                # Stream to client
                yield format_sse_event(event_type, event_data)

            if actual_state.get("is_complete"):
                await SessionService.update_session_costs(
                    db, session_id,
                    actual_state["total_tokens"],
                    actual_state["estimated_cost_usd"]
                )
                break

    except Exception as e:
        # Stream error event
        error_msg = f"{type(e).__name__}: {str(e)}"
        yield create_error_event(error_msg)


@router.post("/generate")
async def generate_code(request: GenerateRequest, db: AsyncSession = Depends(get_db)):
    """Generate Python code from natural language description with SSE streaming.

    This endpoint:
    1. Accepts a coding task description
    2. Streams real-time updates via Server-Sent Events (SSE)
    3. Persists session and messages to database
    4. Returns working Python code with test validation

    Event types emitted:
    - session_created: New session created (if no session_id provided)
    - planning: Problem understanding and approach
    - test_inference: Generated test cases (or test_inference_skipped)
    - code_generated: Generated code (versioned)
    - execution: Code execution results
    - validation: Test validation results
    - error_fixing: Error analysis (if retrying)
    - cost_update: Token usage and cost updates
    - complete: Final results
    - error: Error occurred

    Args:
        request: GenerateRequest with query and configuration
        db: Database session (injected)

    Returns:
        StreamingResponse with Server-Sent Events
    """
    # Validate request
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Return SSE stream
    return StreamingResponse(
        generate_code_stream(request, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
