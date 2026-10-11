"""
Supabase Client Service for The Lenny Growth Assistant.
Manages realtime two-way sync and persistence to Supabase project hbuevcxmlmysbhfiknsn.supabase.co.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from supabase import create_client, Client
from app.config import settings
from app.logging import logger


class SupabaseSyncService:
    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_key
        self._client: Optional[Client] = None

        if self.url and self.key:
            try:
                self._client = create_client(self.url, self.key)
                logger.info("supabase_client_connected", url=self.url)
            except Exception as e:
                logger.warning("supabase_init_failed", error=str(e))

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def sync_chat(
        self,
        chat_id: str,
        title: str,
        plan_tier: str = "free",
        model: str = "qwen2.5:3b",
        provider: str = "ollama",
        storage_archive_url: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        """Upserts a chat into Supabase public.chats."""
        if not self._client:
            return False
        try:
            created_iso = created_at.isoformat() if created_at else datetime.now(timezone.utc).isoformat()
            updated_iso = updated_at.isoformat() if updated_at else datetime.now(timezone.utc).isoformat()
            payload = {
                "id": chat_id,
                "user_id": "Vetrii",
                "title": title or "New Chat",
                "plan_tier": plan_tier or "free",
                "provider": provider or "ollama",
                "model": model or "qwen2.5:3b",
                "s3_archive_url": storage_archive_url,
                "created_at": created_iso,
                "updated_at": updated_iso,
            }
            self._client.table("chats").upsert(payload).execute()
            logger.info("supabase_chat_synced", chat_id=chat_id)
            return True
        except Exception as e:
            logger.warning("supabase_sync_chat_notice", error=str(e), chat_id=chat_id)
            return False

    async def sync_message(
        self,
        message_id: str,
        chat_id: str,
        role: str,
        content: str,
        thought: Optional[str] = None,
        citations: Optional[list] = None,
        created_at: Optional[datetime] = None,
    ) -> bool:
        """Inserts/upserts a message into Supabase public.chat_history."""
        if not self._client:
            return False
        try:
            created_iso = created_at.isoformat() if created_at else datetime.now(timezone.utc).isoformat()
            payload = {
                "id": message_id,
                "chat_id": chat_id,
                "role": role,
                "content": content,
                "thought": thought,
                "citations": citations or [],
                "created_at": created_iso,
            }
            self._client.table("chat_history").upsert(payload).execute()
            logger.info("supabase_message_synced", message_id=message_id, chat_id=chat_id)
            return True
        except Exception as e:
            logger.warning("supabase_sync_message_notice", error=str(e), message_id=message_id)
            return False

    async def sync_response_metric(
        self,
        chat_id: str,
        message_id: Optional[str],
        model_used: str,
        latency_ms: int,
        tokens_per_second: float = 0.0,
        status: str = "success",
        provider: str = "ollama",
        created_at: Optional[datetime] = None,
    ) -> bool:
        """Inserts latency and performance metrics into Supabase public.responses_and_times."""
        if not self._client:
            return False
        try:
            created_iso = created_at.isoformat() if created_at else datetime.now(timezone.utc).isoformat()
            payload = {
                "chat_id": chat_id,
                "message_id": message_id,
                "model_used": model_used,
                "provider": provider,
                "latency_ms": latency_ms,
                "tokens_per_second": tokens_per_second,
                "status": status,
                "created_at": created_iso,
            }
            self._client.table("responses_and_times").insert(payload).execute()
            return True
        except Exception as e:
            logger.warning("supabase_sync_metrics_notice", error=str(e))
            return False

    async def sync_token_usage(
        self,
        chat_id: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        plan_type: str = "free",
        cost_usd: float = 0.0,
        provider: str = "ollama",
        created_at: Optional[datetime] = None,
    ) -> bool:
        """Inserts token usage metrics into Supabase public.each_models_history_and_tokens_usage."""
        if not self._client:
            return False
        try:
            created_iso = created_at.isoformat() if created_at else datetime.now(timezone.utc).isoformat()
            payload = {
                "chat_id": chat_id,
                "model_name": model_name,
                "provider": provider,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "plan_type": plan_type,
                "cost_estimate_usd": cost_usd,
                "created_at": created_iso,
            }
            self._client.table("each_models_history_and_tokens_usage").insert(payload).execute()
            return True
        except Exception as e:
            logger.warning("supabase_sync_tokens_notice", error=str(e))
            return False

    async def sync_file_upload(
        self,
        chat_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        storage_path: Optional[str] = None,
        storage_url: Optional[str] = None,
        extracted_text: Optional[str] = None,
        generation_type: Optional[str] = None,
        generated_content: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> bool:
        """Inserts uploaded file/artifact into Supabase public.file_uploads_and_generations."""
        if not self._client:
            return False
        try:
            created_iso = created_at.isoformat() if created_at else datetime.now(timezone.utc).isoformat()
            payload = {
                "chat_id": chat_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size_bytes": file_size,
                "s3_key": storage_path,
                "s3_url": storage_url,
                "extracted_text": extracted_text,
                "generation_type": generation_type,
                "generated_content": generated_content,
                "created_at": created_iso,
            }
            self._client.table("file_uploads_and_generations").insert(payload).execute()
            return True
        except Exception as e:
            logger.warning("supabase_sync_file_notice", error=str(e))
            return False

    async def delete_chat(self, chat_id: str) -> bool:
        """Deletes a chat from Supabase (cascades automatically to all related tables)."""
        if not self._client:
            return False
        try:
            self._client.table("chats").delete().eq("id", chat_id).execute()
            logger.info("supabase_chat_deleted", chat_id=chat_id)
            return True
        except Exception as e:
            logger.warning("supabase_delete_chat_notice", error=str(e), chat_id=chat_id)
            return False

    async def clear_all_chats(self) -> bool:
        """Clears all chats and related records from Supabase."""
        if not self._client:
            return False
        try:
            self._client.table("chats").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            logger.info("supabase_all_chats_cleared")
            return True
        except Exception as e:
            logger.warning("supabase_clear_all_notice", error=str(e))
            return False

    async def test_connection(self) -> Dict[str, Any]:
        """Tests live connectivity to Supabase Database and Storage."""
        if not self._client:
            return {"connected": False, "error": "Client not initialized (check SUPABASE_URL and SUPABASE_KEY)"}
        try:
            res = self._client.table("chats").select("id").limit(1).execute()
            return {"connected": True, "status": "ok", "url": self.url}
        except Exception as e:
            return {"connected": False, "error": str(e), "url": self.url}


supabase_service = SupabaseSyncService()
