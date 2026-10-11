"""
Chats and File Uploads API Endpoints for Supabase and S3 storage.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, desc, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Chat, ChatHistory, FileUploadGeneration, ResponseTime, ModelHistoryTokenUsage
from app.storage.supabase_storage import supabase_storage_service
from app.db.supabase_client import supabase_service
from app.config import settings

router = APIRouter(prefix="/chats", tags=["Chats & Storage"])


@router.post("")
async def create_chat(
    title: Optional[str] = "New Chat",
    plan_tier: Optional[str] = "free",
    model: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    chat = Chat(
        title=title or "New Chat",
        plan_tier=plan_tier or "free",
        provider=settings.llm_provider,
        model=model or settings.llm_model
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    # Real-time sync to Supabase
    await supabase_service.sync_chat(
        chat_id=chat.id,
        title=chat.title,
        plan_tier=chat.plan_tier,
        model=chat.model,
        provider=chat.provider,
        created_at=chat.created_at,
        updated_at=chat.updated_at
    )

    return {
        "id": chat.id,
        "title": chat.title,
        "plan_tier": chat.plan_tier,
        "model": chat.model,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "message_count": 0
    }


@router.get("")
async def list_chats(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Chat, func.count(ChatHistory.id).label("msg_count"))
        .outerjoin(ChatHistory, Chat.id == ChatHistory.chat_id)
        .group_by(Chat.id)
        .order_by(desc(Chat.updated_at))
    )
    result = await db.execute(stmt)
    chats = []
    for chat, count in result.all():
        chats.append({
            "id": chat.id,
            "title": chat.title,
            "plan_tier": chat.plan_tier,
            "model": chat.model,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "message_count": count
        })
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Chat)
        .options(selectinload(Chat.messages))
        .where(Chat.id == chat_id)
    )
    res = await db.execute(stmt)
    chat = res.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = [
        {
            "id": m.id,
            "chat_id": m.chat_id,
            "role": m.role,
            "content": m.content,
            "thought": m.thought,
            "citations": m.citations,
            "created_at": m.created_at
        }
        for m in chat.messages
    ]

    return {
        "id": chat.id,
        "title": chat.title,
        "plan_tier": chat.plan_tier,
        "model": chat.model,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "messages": messages
    }


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    await db.delete(chat)
    await db.commit()
    await supabase_service.delete_chat(chat_id)
    return {"status": "ok", "message": f"Chat {chat_id} deleted."}


@router.delete("")
async def clear_all_chats(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Chat))
    await db.commit()
    await supabase_service.clear_all_chats()
    return {"status": "ok", "message": "All chats cleared."}


@router.post("/{chat_id}/upload")
async def upload_file_to_chat(
    chat_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    file_bytes = await file.read()
    storage_res = await supabase_storage_service.upload_file(
        file_name=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream"
    )

    # Save to file_uploads_and_generations table
    record = FileUploadGeneration(
        chat_id=chat_id,
        file_name=file.filename,
        file_type=file.content_type or "unknown",
        file_size_bytes=len(file_bytes),
        storage_path=storage_res.get("storage_path"),
        storage_url=storage_res.get("storage_url")
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "file_name": record.file_name,
        "file_type": record.file_type,
        "file_size": record.file_size_bytes,
        "storage_url": record.storage_url
    }
