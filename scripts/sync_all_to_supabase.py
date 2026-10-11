"""
Sync all historical SQLite records to Supabase tables:
- public.chats
- public.chat_history
- public.responses_and_times
- public.each_models_history_and_tokens_usage
- public.file_uploads_and_generations
"""
import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.db.supabase_client import supabase_service

def sync_sqlite_to_supabase():
    client = supabase_service._client
    if not client:
        print("ERROR: Supabase client not initialized.")
        return

    conn = sqlite3.connect("lenny_growth.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Sync Chats
    print("--- 1. Syncing Chats ---")
    cur.execute("SELECT * FROM chats")
    chat_rows = cur.fetchall()
    print(f"Found {len(chat_rows)} chats in SQLite.")
    chat_payloads = []
    for r in chat_rows:
        # Check archive url
        archive_url = None
        try:
            archive_url = r["s3_archive_url"]
        except Exception:
            try:
                archive_url = r["storage_archive_url"]
            except Exception:
                pass

        chat_payloads.append({
            "id": r["id"],
            "user_id": r["user_id"] or "Vetrii",
            "title": r["title"] or "New Chat",
            "plan_tier": r["plan_tier"] or "free",
            "provider": r["provider"] or "ollama",
            "model": r["model"] or "qwen2.5:3b",
            "s3_archive_url": archive_url,
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        })
    if chat_payloads:
        for i in range(0, len(chat_payloads), 50):
            chunk = chat_payloads[i:i+50]
            client.table("chats").upsert(chunk).execute()
        print(f"Successfully upserted {len(chat_payloads)} chats to Supabase.")

    # 2. Sync Chat History (Messages)
    print("--- 2. Syncing Chat History ---")
    cur.execute("SELECT * FROM chat_history")
    msg_rows = cur.fetchall()
    print(f"Found {len(msg_rows)} messages in SQLite.")
    msg_payloads = []
    for r in msg_rows:
        citations = []
        if r["citations"]:
            try:
                citations = json.loads(r["citations"]) if isinstance(r["citations"], str) else r["citations"]
            except Exception:
                citations = []
        msg_payloads.append({
            "id": r["id"],
            "chat_id": r["chat_id"],
            "role": r["role"],
            "content": r["content"],
            "thought": r["thought"],
            "citations": citations,
            "created_at": r["created_at"],
        })
    if msg_payloads:
        for i in range(0, len(msg_payloads), 50):
            chunk = msg_payloads[i:i+50]
            client.table("chat_history").upsert(chunk).execute()
        print(f"Successfully upserted {len(msg_payloads)} messages to Supabase.")

    # 3. Sync Responses & Times
    print("--- 3. Syncing Responses & Times ---")
    cur.execute("SELECT * FROM responses_and_times")
    resp_rows = cur.fetchall()
    print(f"Found {len(resp_rows)} response metrics in SQLite.")
    resp_payloads = []
    for r in resp_rows:
        resp_payloads.append({
            "id": r["id"],
            "chat_id": r["chat_id"],
            "message_id": r["message_id"],
            "model_used": r["model_used"],
            "provider": r["provider"] or "ollama",
            "latency_ms": r["latency_ms"],
            "tokens_per_second": r["tokens_per_second"],
            "time_to_first_token_ms": r["time_to_first_token_ms"],
            "status": r["status"] or "success",
            "created_at": r["created_at"],
        })
    if resp_payloads:
        for i in range(0, len(resp_payloads), 50):
            chunk = resp_payloads[i:i+50]
            client.table("responses_and_times").upsert(chunk).execute()
        print(f"Successfully upserted {len(resp_payloads)} metrics to Supabase.")

    # 4. Sync Token Usage
    print("--- 4. Syncing Token Usage ---")
    cur.execute("SELECT * FROM each_models_history_and_tokens_usage")
    token_rows = cur.fetchall()
    print(f"Found {len(token_rows)} token usage records in SQLite.")
    token_payloads = []
    for r in token_rows:
        token_payloads.append({
            "id": r["id"],
            "chat_id": r["chat_id"],
            "model_name": r["model_name"],
            "provider": r["provider"] or "ollama",
            "prompt_tokens": r["prompt_tokens"] or 0,
            "completion_tokens": r["completion_tokens"] or 0,
            "total_tokens": r["total_tokens"] or 0,
            "plan_type": r["plan_type"] or "free",
            "cost_estimate_usd": r["cost_estimate_usd"] or 0.0,
            "created_at": r["created_at"],
        })
    if token_payloads:
        for i in range(0, len(token_payloads), 50):
            chunk = token_payloads[i:i+50]
            client.table("each_models_history_and_tokens_usage").upsert(chunk).execute()
        print(f"Successfully upserted {len(token_payloads)} token usage records to Supabase.")

    # 5. Sync File Uploads
    print("--- 5. Syncing File Uploads ---")
    cur.execute("SELECT * FROM file_uploads_and_generations")
    upload_rows = cur.fetchall()
    print(f"Found {len(upload_rows)} file uploads in SQLite.")
    upload_payloads = []
    for r in upload_rows:
        s3_key = None
        s3_url = None
        try:
            s3_key = r["s3_key"]
            s3_url = r["s3_url"]
        except Exception:
            try:
                s3_key = r["storage_path"]
                s3_url = r["storage_url"]
            except Exception:
                pass
        upload_payloads.append({
            "id": r["id"],
            "chat_id": r["chat_id"],
            "file_name": r["file_name"],
            "file_type": r["file_type"],
            "file_size_bytes": r["file_size_bytes"] or 0,
            "s3_key": s3_key,
            "s3_url": s3_url,
            "extracted_text": r["extracted_text"],
            "generation_type": r["generation_type"],
            "generated_content": r["generated_content"],
            "created_at": r["created_at"],
        })
    if upload_payloads:
        for i in range(0, len(upload_payloads), 50):
            chunk = upload_payloads[i:i+50]
            client.table("file_uploads_and_generations").upsert(chunk).execute()
        print(f"Successfully upserted {len(upload_payloads)} file uploads to Supabase.")

    conn.close()
    print("\n>>> ALL SQLite DATA SUCCESSFULLY SYNCED TO SUPABASE <<<")

if __name__ == "__main__":
    sync_sqlite_to_supabase()
