"""
Abstract LLM Provider interface.
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        """Stream generated tokens as an async generator."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> str:
        """Generate complete text synchronously or in a single call."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if provider endpoint and model are healthy."""
        pass
