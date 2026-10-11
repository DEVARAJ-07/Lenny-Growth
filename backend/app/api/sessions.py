"""
Sessions API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Session, Message, User
from app.schemas.api_schemas import SessionCreate, SessionDetailResponse, SessionSummary, MessageResponse
from app.db.supabase_client import supabase_service
from app.config import settings

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionSummary)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    # Check or create default user if provided
    user_id = payload.user_id
    if user_id:
        u = await db.get(User, user_id)
        if not u:
            u = User(id=user_id, external_id=user_id)
            db.add(u)
            await db.flush()

    sess = Session(
        title=payload.title or "New Chat",
        user_id=user_id,
        provider=payload.provider or settings.llm_provider,
        model=payload.model or settings.llm_model
    )
    db.add(sess)
    await db.commit()
    await db.refresh(sess)

    # Real-time sync to Supabase
    await supabase_service.sync_chat(
        chat_id=sess.id,
        title=sess.title,
        plan_tier=sess.plan_tier,
        model=sess.model,
        provider=sess.provider,
        created_at=sess.created_at,
        updated_at=sess.updated_at
    )

    return SessionSummary(
        id=sess.id,
        title=sess.title,
        provider=sess.provider,
        model=sess.model,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        message_count=0
    )


@router.get("", response_model=List[SessionSummary])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session, func.count(Message.id).label("msg_count"))
        .outerjoin(Message, Session.id == Message.chat_id)
        .group_by(Session.id)
        .order_by(desc(Session.updated_at))
    )
    result = await db.execute(stmt)
    sessions_with_counts = []
    for sess, count in result.all():
        sessions_with_counts.append(
            SessionSummary(
                id=sess.id,
                title=sess.title,
                provider=sess.provider,
                model=sess.model,
                created_at=sess.created_at,
                updated_at=sess.updated_at,
                message_count=count
            )
        )
    return sessions_with_counts


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session)
        .options(selectinload(Session.messages))
        .where(Session.id == session_id)
    )
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_data = [
        MessageResponse(
            id=m.id,
            session_id=m.chat_id,
            role=m.role,
            content=m.content,
            citations=m.citations,
            route=None,
            latency_ms=None,
            created_at=m.created_at
        )
        for m in sess.messages
    ]

    return SessionDetailResponse(
        id=sess.id,
        user_id=sess.user_id,
        title=sess.title,
        provider=sess.provider,
        model=sess.model,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        messages=messages_data
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    sess = await db.get(Session, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(sess)
    await db.commit()
    await supabase_service.delete_chat(session_id)
    return {"status": "ok", "message": f"Session {session_id} deleted."}


@router.delete("")
async def clear_all_history(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Session))
    await db.commit()
    await supabase_service.clear_all_chats()
    return {"status": "ok", "message": "All session history cleared."}
