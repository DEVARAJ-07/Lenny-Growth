"""
LLM Provider Factory with automatic model mapping and fallback.
"""
from typing import Optional
from app.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.ollama import OllamaProvider
from app.llm.anthropic import AnthropicProvider
from app.logging import logger


class LLMFactory:
    @classmethod
    def get_provider(
        cls,
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None
    ) -> BaseLLMProvider:
        chosen_model = override_model or settings.llm_model
        provider_name = (override_provider or settings.llm_provider).lower()

        # If user explicitly requested Claude or Anthropic
        if provider_name == "anthropic" or (override_model and "claude" in override_model.lower()):
            if settings.anthropic_api_key and len(settings.anthropic_api_key) > 5:
                return AnthropicProvider(default_model=chosen_model)
            logger.info("anthropic_key_missing_falling_back_to_local_ollama", fallback_model=chosen_model)
            return OllamaProvider(default_model=chosen_model)

        # Default local Ollama (qwen2.5:3b, deepseek-r1:1.5b, llama3.2:3b)
        return OllamaProvider(default_model=chosen_model)
