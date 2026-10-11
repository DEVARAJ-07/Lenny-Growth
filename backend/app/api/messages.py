"""
Streaming messages endpoint using Server-Sent Events (SSE).
"""
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, async_session_factory
from app.db.models import Session, Message
from app.schemas.api_schemas import MessageCreate
from app.agent.orchestrator import agent_orchestrator
from app.db.supabase_client import supabase_service
from app.logging import logger

router = APIRouter(prefix="/sessions", tags=["Messages"])


@router.post("/{session_id}/messages")
async def send_message_stream(
    session_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify session exists
    sess = await db.get(Session, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    # If first message, auto-update title based on first 6 words of user prompt
    if sess.title == "New Chat":
        words = payload.content.strip().split()
        sess.title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")

    # Save user message
    user_msg = Message(
        chat_id=session_id,
        role="user",
        content=payload.content
    )
    db.add(user_msg)
    await db.commit()

    # Real-time sync to Supabase
    await supabase_service.sync_message(
        message_id=user_msg.id,
        chat_id=session_id,
        role="user",
        content=payload.content,
        created_at=user_msg.created_at
    )
    await supabase_service.sync_chat(
        chat_id=sess.id,
        title=sess.title,
        plan_tier=sess.plan_tier,
        model=sess.model,
        provider=sess.provider,
        updated_at=sess.updated_at
    )

    async def sse_event_generator():
        # Open independent async DB session for streaming
        async with async_session_factory() as stream_db:
            try:
                async for event in agent_orchestrator.process_message_stream(
                    session_id=session_id,
                    user_query=payload.content,
                    db_session=stream_db,
                    provider_override=payload.provider,
                    model_override=payload.model
                ):
                    event_data = json.dumps(event)
                    yield f"data: {event_data}\n\n"
                    await asyncio.sleep(0.005)  # smooth SSE packet flush
            except Exception as e:
                logger.exception("streaming_error", error=str(e), session_id=session_id)
                error_payload = json.dumps({
                    "type": "error",
                    "error": {
                        "code": "STREAMING_ERROR",
                        "message": str(e),
                        "hint": "Check model availability and backend logs."
                    }
                })
                yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
