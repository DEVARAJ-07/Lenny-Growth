"""
Batch Ingestion for Lenny's Podcast Transcripts.
Ingests iconic product & growth episodes with batch vector embeddings and metadata.
"""
import os
import glob
import asyncio
import time
from app.db.session import async_session_factory, init_db
from app.retrieval.ingest import ingest_single_file
from app.logging import logger

KEY_GUEST_SLUGS = [
    "elena-verna",
    "shreyas-doshi",
    "brian-chesky",
    "adam-fishman",
    "hila-qu",
    "casey-winters",
    "fareed-mosavat",
    "gustaf-alstromer",
    "andy-johns",
    "april-dunford",
    "bangaly-kaba",
    "gibson-biddle",
    "bob-moesta",
    "eoghan-mccabe",
    "geoffrey-moore",
    "marty-cagan",
    "melissa-perri",
    "teresa-torres",
    "annie-duke",
    "ami-vora",
    "ada-chen-rekhi",
    "adam-grenier",
    "austin-hay",
    "dan-hockenmaier",
    "ethan-smith",
    "gagan-biyani",
    "ken-norton",
    "kevin-weil",
    "madhavan-ramanujam",
    "archie-abrams",
    "albert-cheng",
    "amjad-masad",
]

async def run_targeted_ingest():
    await init_db()
    base_dir = "data/transcripts/raw/episodes"
    target_files = []

    # Find paths for key guests
    for slug in KEY_GUEST_SLUGS:
        p = os.path.join(base_dir, slug, "transcript.md")
        if os.path.exists(p):
            target_files.append(p)
        else:
            # Check for partial matches
            matches = glob.glob(os.path.join(base_dir, f"{slug}*", "transcript.md"))
            target_files.extend(matches)

    # De-duplicate
    target_files = sorted(list(set(target_files)))
    print(f"Targeting {len(target_files)} key episode transcripts for ingestion...")

    total_chunks = 0
    total_docs = 0
    t0 = time.time()

    async with async_session_factory() as session:
        for idx, file_path in enumerate(target_files):
            try:
                c = await ingest_single_file(file_path, session)
                if c is not None and c > 0:
                    total_chunks += c
                    total_docs += 1
                    print(f"[{idx+1}/{len(target_files)}] Ingested {os.path.basename(os.path.dirname(file_path))} ({c} chunks)")
                else:
                    print(f"[{idx+1}/{len(target_files)}] Skipped/already ingested {os.path.basename(os.path.dirname(file_path))}")
            except Exception as e:
                print(f"Error on {file_path}: {e}")

    elapsed = round(time.time() - t0, 2)
    print(f"\nTargeted Ingestion Complete: {total_docs} new documents, {total_chunks} new chunks in {elapsed}s.")

if __name__ == "__main__":
    asyncio.run(run_targeted_ingest())
