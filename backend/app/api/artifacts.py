"""
Artifacts API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Artifact
from app.schemas.api_schemas import ArtifactResponse

router = APIRouter(tags=["Artifacts"])


@router.get("/sessions/{session_id}/artifacts", response_model=List[ArtifactResponse])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Artifact)
        .where(Artifact.session_id == session_id)
        .order_by(desc(Artifact.created_at))
    )
    res = await db.execute(stmt)
    artifacts = res.scalars().all()
    return [
        ArtifactResponse(
            id=a.id,
            session_id=a.session_id,
            message_id=a.message_id,
            type=a.type,
            title=a.title,
            content=a.content,
            created_at=a.created_at
        )
        for a in artifacts
    ]


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    art = await db.get(Artifact, artifact_id)
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactResponse(
        id=art.id,
        session_id=art.session_id,
        message_id=art.message_id,
        type=art.type,
        title=art.title,
        content=art.content,
        created_at=art.created_at
    )
