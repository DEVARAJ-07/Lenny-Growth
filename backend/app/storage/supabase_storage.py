"""
Supabase Storage Client for Chat History, Artifacts, and Uploads.
Replaces AWS S3 with native Supabase Storage buckets.
"""
import os
import json
import io
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.config import settings
from app.logging import logger
from app.db.supabase_client import supabase_service


class SupabaseStorageService:
    def __init__(self):
        self.bucket_name = settings.supabase_storage_bucket
        self._ensure_local_fallback_dir()

    def _ensure_local_fallback_dir(self):
        self.local_dir = os.path.join("data", "supabase_storage_local")
        os.makedirs(self.local_dir, exist_ok=True)
        os.makedirs(os.path.join(self.local_dir, "chats"), exist_ok=True)
        os.makedirs(os.path.join(self.local_dir, "uploads"), exist_ok=True)

    async def archive_chat(
        self,
        chat_id: str,
        chat_title: str,
        history: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Archives a complete chat thread as JSON into Supabase Storage.
        Falls back seamlessly to local persistent storage if Supabase credentials are not connected.
        """
        payload = {
            "chat_id": chat_id,
            "title": chat_title,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "messages": history,
        }
        json_bytes = json.dumps(payload, indent=2).encode("utf-8")
        file_path = f"chats/{chat_id}.json"

        # 1. Try Supabase Storage
        if supabase_service.is_connected and supabase_service._client:
            try:
                # Ensure bucket exists
                try:
                    supabase_service._client.storage.get_bucket(self.bucket_name)
                except Exception:
                    try:
                        supabase_service._client.storage.create_bucket(
                            self.bucket_name,
                            options={"public": True}
                        )
                    except Exception:
                        pass

                # Upload to Supabase Storage
                supabase_service._client.storage.from_(self.bucket_name).upload(
                    file_path,
                    json_bytes,
                    file_options={"content-type": "application/json", "upsert": "true"}
                )
                public_url = supabase_service._client.storage.from_(self.bucket_name).get_public_url(file_path)
                logger.info("chat_archived_to_supabase_storage", url=public_url, chat_id=chat_id)
                return public_url
            except Exception as e:
                logger.warning("supabase_storage_upload_warning", error=str(e), chat_id=chat_id)

        # 2. Local Fallback Persistence
        local_file = os.path.join(self.local_dir, "chats", f"{chat_id}.json")
        with open(local_file, "wb") as f:
            f.write(json_bytes)
        local_url = f"file://{os.path.abspath(local_file)}"
        logger.info("chat_archived_locally", path=local_url, chat_id=chat_id)
        return local_url

    async def upload_file(
        self,
        file_name: str,
        file_bytes: bytes,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Uploads a user-attached document or generated artifact to Supabase Storage.
        """
        timestamp = int(datetime.now(timezone.utc).timestamp())
        storage_path = f"uploads/{timestamp}_{file_name}"

        # 1. Try Supabase Storage
        if supabase_service.is_connected and supabase_service._client:
            try:
                try:
                    supabase_service._client.storage.get_bucket(self.bucket_name)
                except Exception:
                    try:
                        supabase_service._client.storage.create_bucket(
                            self.bucket_name,
                            options={"public": True}
                        )
                    except Exception:
                        pass

                supabase_service._client.storage.from_(self.bucket_name).upload(
                    storage_path,
                    file_bytes,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                public_url = supabase_service._client.storage.from_(self.bucket_name).get_public_url(storage_path)
                logger.info("file_uploaded_to_supabase_storage", url=public_url, path=storage_path)
                return {
                    "storage_path": storage_path,
                    "storage_url": public_url,
                    "storage_provider": "supabase"
                }
            except Exception as e:
                logger.warning("supabase_storage_file_upload_warning", error=str(e))

        # 2. Local Fallback Persistence
        local_file = os.path.join(self.local_dir, "uploads", f"{timestamp}_{file_name}")
        with open(local_file, "wb") as f:
            f.write(file_bytes)
        local_url = f"file://{os.path.abspath(local_file)}"
        return {
            "storage_path": storage_path,
            "storage_url": local_url,
            "storage_provider": "local"
        }


supabase_storage_service = SupabaseStorageService()
