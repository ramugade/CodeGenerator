from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.db.models import Session, Message, TokenUsage

class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, title: str, llm_provider: str):
        session = Session(title=title[:200], llm_provider=llm_provider)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session(db: AsyncSession, session_id: str):
        stmt = select(Session).where(Session.id == session_id).options(
            selectinload(Session.messages),
            selectinload(Session.token_usages)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sessions(db: AsyncSession, limit: int = 50):
        stmt = select(Session).order_by(desc(Session.updated_at)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def save_message(db: AsyncSession, session_id: str,
                          message_type: str, content: dict, order_index: int):
        message = Message(
            session_id=session_id,
            message_type=message_type,
            content=content,
            order_index=order_index
        )
        db.add(message)
        await db.commit()

    @staticmethod
    async def save_token_usage(db: AsyncSession, session_id: str,
                              step_name: str, token_data: dict):
        """Save token usage. token_data must include: prompt_tokens, completion_tokens,
        total_tokens, cost_usd, model, provider"""
        usage = TokenUsage(session_id=session_id, step_name=step_name, **token_data)
        db.add(usage)
        await db.commit()

    @staticmethod
    async def update_session_costs(db: AsyncSession, session_id: str,
                                   total_tokens: int, total_cost: float):
        stmt = select(Session).where(Session.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            session.total_tokens = total_tokens
            session.total_cost_usd = total_cost
            session.updated_at = datetime.utcnow()
            await db.commit()
