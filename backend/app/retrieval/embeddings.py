"""
Embedding generator using local Ollama nomic-embed-text.
"""
from typing import List, Optional
import httpx
from app.config import settings
from app.errors import AppError
from app.logging import logger


class EmbeddingClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.embedding_model

    async def get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embed"
        payload = {"model": self.model, "input": text}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    embs = data.get("embeddings", [])
                    if embs:
                        return embs[0]
                # Fallback to /api/embeddings
                fallback_res = await client.post(f"{self.base_url}/api/embeddings", json={"model": self.model, "prompt": text})
                if fallback_res.status_code == 200:
                    return fallback_res.json().get("embedding", [])
                raise AppError(
                    code="EMBEDDING_FAILED",
                    message=f"Embedding generation failed: HTTP {res.status_code}",
                    hint=f"Ensure '{self.model}' is pulled via `ollama pull {self.model}`."
                )
        except httpx.ConnectError:
            raise AppError(
                code="OLLAMA_SERVICE_UNAVAILABLE",
                message=f"Cannot connect to Ollama embedding service at {self.base_url}.",
                hint="Ensure Ollama daemon is running."
            )

    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []
        url = f"{self.base_url}/api/embed"
        results = []
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for i in range(0, len(texts), batch_size):
                    chunk = texts[i:i + batch_size]
                    try:
                        res = await client.post(url, json={"model": self.model, "input": chunk})
                        if res.status_code == 200:
                            data = res.json()
                            results.extend(data.get("embeddings", []))
                            continue
                    except Exception:
                        pass
                    # Per-item fallback
                    for t in chunk:
                        results.append(await self.get_embedding(t))
        except Exception:
            for t in texts:
                results.append(await self.get_embedding(t))
        return results


embedding_client = EmbeddingClient()
