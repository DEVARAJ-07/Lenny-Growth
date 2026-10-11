"""
Anthropic Claude Provider implementation.
"""
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx
from app.llm.base import BaseLLMProvider
from app.config import settings
from app.errors import AppError
from app.logging import logger


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or settings.anthropic_api_key
        self.default_model = default_model

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise AppError(
                code="ANTHROPIC_KEY_MISSING",
                message="Anthropic API key is not configured.",
                hint="Set ANTHROPIC_API_KEY in .env or switch LLM_PROVIDER to 'ollama'."
            )

        # Convert messages format (extract system prompt if present)
        system_content = ""
        user_assistant_messages = []
        for m in messages:
            if m["role"] == "system":
                system_content += m["content"] + "\n"
            else:
                user_assistant_messages.append({"role": m["role"], "content": m["content"]})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model or self.default_model,
            "messages": user_assistant_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        if system_content:
            payload["system"] = system_content.strip()

        url = "https://api.anthropic.com/v1/messages"
        async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err = await response.aread()
                    raise AppError(
                        code="ANTHROPIC_API_ERROR",
                        message=f"Anthropic returned HTTP {response.status_code}: {err.decode('utf-8', errors='ignore')}",
                        hint="Check your ANTHROPIC_API_KEY or model identifier."
                    )
                import json
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            event = json.loads(data_str)
                            if event.get("type") == "content_block_delta":
                                text = event.get("delta", {}).get("text", "")
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            continue

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> str:
        tokens = []
        async for token in self.generate_stream(messages, model, temperature, max_tokens):
            tokens.append(token)
        return "".join(tokens)

    async def check_health(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)
