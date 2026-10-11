"""
Transcript Ingestion Pipeline.
Loads episodes from data/transcripts/raw/episodes, chunks, computes embeddings,
and idempotently persists documents and chunks.
"""
import os
import glob
import asyncio
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_factory, init_db
from app.db.models import Document, Chunk
from app.retrieval.chunking import chunk_transcript, ParsedTranscript
from app.retrieval.embeddings import embedding_client
from app.logging import logger


async def ingest_single_file(file_path: str, session: AsyncSession) -> Optional[int]:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        logger.error("file_read_error", path=file_path, error=str(e))
        return None

    parsed: ParsedTranscript = chunk_transcript(file_path, content)

    # Idempotent check
    stmt = select(Document).where(Document.content_hash == parsed.content_hash)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        logger.debug("skipping_unchanged_document", title=parsed.title, guest=parsed.guest)
        return 0

    # Create Document record
    doc = Document(
        title=parsed.title,
        guest=parsed.guest,
        source_path=file_path,
        source_url=parsed.youtube_url,
        content_hash=parsed.content_hash
    )
    session.add(doc)
    await session.flush()  # populate doc.id

    # Compute embeddings in batches
    texts = [c.text for c in parsed.chunks]
    embeddings = await embedding_client.get_embeddings_batch(texts)

    # Save chunks
    for parsed_chunk, emb in zip(parsed.chunks, embeddings):
        chunk_rec = Chunk(
            document_id=doc.id,
            chunk_index=parsed_chunk.chunk_index,
            text=parsed_chunk.text,
            speaker=parsed_chunk.speaker,
            start_ref=parsed_chunk.start_ref,
            embedding=emb
        )
        session.add(chunk_rec)

    await session.commit()
    logger.info("ingested_document", title=parsed.title, guest=parsed.guest, chunks=len(parsed.chunks))
    return len(parsed.chunks)


async def run_ingestion(transcripts_dir: str = "data/transcripts/raw/episodes", limit: Optional[int] = None):
    await init_db()
    pattern = os.path.join(transcripts_dir, "*", "transcript.md")
    files = glob.glob(pattern)
    logger.info("found_transcript_files", count=len(files))

    if limit:
        files = files[:limit]

    total_chunks = 0
    total_docs = 0

    async with async_session_factory() as session:
        for idx, file_path in enumerate(files):
            count = await ingest_single_file(file_path, session)
            if count is not None and count > 0:
                total_chunks += count
                total_docs += 1
            if (idx + 1) % 10 == 0:
                logger.info("ingestion_progress", processed=idx + 1, total=len(files))

    logger.info("ingestion_completed", total_docs=total_docs, total_chunks=total_chunks)
    return {"documents": total_docs, "chunks": total_chunks}


if __name__ == "__main__":
    import sys
    limit_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(run_ingestion(limit=limit_arg))
