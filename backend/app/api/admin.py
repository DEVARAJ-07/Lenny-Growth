"""
Admin ingestion API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.retrieval.ingest import run_ingestion
from app.logging import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


class IngestRequest(BaseModel):
    limit: Optional[int] = None
    force_refresh: bool = False


@router.post("/ingest")
async def trigger_ingestion(payload: IngestRequest, background_tasks: BackgroundTasks):
    logger.info("triggering_ingestion_background_job", limit=payload.limit)
    background_tasks.add_task(run_ingestion, limit=payload.limit)
    return {
        "status": "queued",
        "message": f"Ingestion task started in background (limit={payload.limit})."
    }
