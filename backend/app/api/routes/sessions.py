from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.session_service import SessionService
from app.models.schemas import SessionResponse, SessionListResponse, MessageDTO

router = APIRouter()

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(db: AsyncSession = Depends(get_db)):
    sessions = await SessionService.list_sessions(db)
    return SessionListResponse(
        sessions=[
            SessionResponse(
                session_id=s.id,
                title=s.title,
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
                status=s.status,
                llm_provider=s.llm_provider,
                total_tokens=s.total_tokens,
                total_cost_usd=s.total_cost_usd,
                iterations=s.iterations_count,
                messages=None  # Don't load messages for list view
            ) for s in sessions
        ]
    )

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Convert DB messages to DTOs ordered by order_index
    message_dtos = [
        MessageDTO(
            type=msg.message_type,
            content=msg.content,
            timestamp=msg.timestamp.isoformat(),
            order=msg.order_index
        )
        for msg in sorted(session.messages, key=lambda m: m.order_index)
    ]

    return SessionResponse(
        session_id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        status=session.status,
        llm_provider=session.llm_provider,
        total_tokens=session.total_tokens,
        total_cost_usd=session.total_cost_usd,
        iterations=session.iterations_count,
        messages=message_dtos
    )

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    await db.delete(session)
    await db.commit()
    return {"message": "Session deleted"}
