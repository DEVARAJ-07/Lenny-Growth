"""
Ollama LLM Provider implementation for local inference with auto-daemon recovery and fallback.
"""
import json
import os
import subprocess
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from app.llm.base import BaseLLMProvider
from app.config import settings
from app.errors import AppError
from app.logging import logger


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.default_model = default_model or settings.llm_model

    def _try_start_ollama_daemon(self):
        """Attempts to start the local Ollama serve process if it is not currently running."""
        try:
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            ollama_exe = os.path.join(local_appdata, "Programs", "Ollama", "ollama.exe")
            if os.path.exists(ollama_exe):
                env = os.environ.copy()
                env["OLLAMA_MODELS"] = settings.ollama_models_path or r"D:\LLMs\ollama_store"
                env["OLLAMA_HOST"] = "127.0.0.1:11434"
                subprocess.Popen(
                    [ollama_exe, "serve"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                logger.info("ollama_daemon_spawn_triggered")
        except Exception as e:
            logger.warning("ollama_daemon_spawn_failed", error=str(e))

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        target_model = model or self.default_model

        # Clean model name mapping
        if "deepseek" in target_model.lower():
            target_model = "deepseek-r1:1.5b"
        elif "llama" in target_model.lower():
            target_model = "llama3.2:3b"
        elif "claude" in target_model.lower():
            # Cloud fallback to best local model if no API key
            target_model = "qwen2.5:3b"
        elif "qwen" in target_model.lower():
            target_model = "qwen2.5:3b"

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        url = f"{self.base_url}/api/chat"
        retries = 1

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
                    async with client.stream("POST", url, json=payload) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            # If model missing, fallback to qwen2.5:3b
                            if attempt == 0:
                                payload["model"] = "qwen2.5:3b"
                                continue
                            raise AppError(
                                code="OLLAMA_HTTP_ERROR",
                                message=f"Ollama returned HTTP {response.status_code}: {error_body.decode('utf-8', errors='ignore')}",
                                hint=f"Model '{target_model}' execution failed."
                            )

                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            try:
                                chunk = json.loads(line)
                                message_chunk = chunk.get("message", {}).get("content", "")
                                if message_chunk:
                                    yield message_chunk
                            except json.JSONDecodeError:
                                continue
                        return  # Successfully finished streaming
            except httpx.ConnectError:
                if attempt == 0:
                    logger.warning("ollama_connect_failed_attempting_daemon_start")
                    self._try_start_ollama_daemon()
                    await asyncio.sleep(2.0)
                    continue

                # Graceful transcript-based fallback if Ollama daemon is completely offline
                yield "I am currently answering from the Lenny Podcast transcript index.\n\n"
                user_question = messages[-1].get("content", "")
                if "TRANSCRIPT EXCERPTS:" in user_question:
                    excerpts = user_question.split("USER QUESTION:")[0].replace("TRANSCRIPT EXCERPTS:", "").strip()
                    yield f"Here is the verified operator wisdom from the transcripts:\n\n{excerpts[:800]}..."
                else:
                    yield "The local Ollama inference service is offline. Please launch `scripts/start-all.ps1` to start the local models."
                return
            except httpx.TimeoutException:
                raise AppError(
                    code="OLLAMA_TIMEOUT",
                    message="Local Ollama generation timed out.",
                    hint="Try shorter prompts or reduce top_k_retrieval context length."
                )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> str:
        collected = []
        async for token in self.generate_stream(messages, model, temperature, max_tokens):
            collected.append(token)
        return "".join(collected)

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False
