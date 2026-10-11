"""
Health check endpoints: /health, /health/db, /health/llm, /health/index, /config.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Document, Chunk
from app.llm.factory import LLMFactory
from app.config import settings
from app.schemas.api_schemas import ConfigResponse

router = APIRouter(tags=["Health & Config"])


@router.get("/health")
async def overall_health(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    provider = LLMFactory.get_provider()
    llm_ok = await provider.check_health()

    status = "healthy" if (db_ok and llm_ok) else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
        "llm": "connected" if llm_ok else "disconnected",
        "active_provider": settings.llm_provider,
        "active_model": settings.llm_model,
    }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "component": "database", "message": "Database connection verified."}
    except Exception as e:
        return {"status": "error", "component": "database", "message": str(e)}


@router.get("/health/llm")
async def health_llm():
    provider = LLMFactory.get_provider()
    ok = await provider.check_health()
    return {
        "status": "ok" if ok else "error",
        "component": "llm",
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "endpoint": settings.ollama_base_url if settings.llm_provider == "ollama" else "cloud"
    }


@router.get("/health/index")
async def health_index(db: AsyncSession = Depends(get_db)):
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    chunk_count = (await db.execute(select(func.count(Chunk.id)))).scalar() or 0
    return {
        "status": "ok",
        "component": "knowledge_index",
        "total_documents": doc_count,
        "total_chunks": chunk_count,
        "embedding_model": settings.embedding_model
    }


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    provider = LLMFactory.get_provider()
    ollama_ok = await provider.check_health()
    return ConfigResponse(
        active_provider=settings.llm_provider,
        active_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        available_providers=["ollama", "anthropic", "openai"],
        local_ollama_available=ollama_ok,
        cloud_anthropic_available=bool(settings.anthropic_api_key),
        cloud_openai_available=bool(settings.openai_api_key),
    )
