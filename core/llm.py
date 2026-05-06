"""LLM Provider abstraction layer."""

from typing import AsyncIterator, Optional
from shared.config import settings
import json


class LLMProvider:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(self, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    """Works with any OpenAI-compatible API (DeepSeek, OpenAI, etc.)."""

    async def chat(self, messages: list[dict], **kwargs) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": kwargs.get("model", self.model),
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "stream": False,
                },
                timeout=120,
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        import httpx
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": kwargs.get("model", self.model),
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "stream": True,
                },
                timeout=120,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            continue


def get_llm(provider: str = None) -> LLMProvider:
    provider = provider or settings.llm_default_provider

    if provider == "deepseek":
        return OpenAICompatibleProvider(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.llm_default_model,
        )
    elif provider == "openai":
        return OpenAICompatibleProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or "https://api.openai.com",
            model=settings.llm_default_model,
        )
    raise ValueError(f"Unknown provider: {provider}")
