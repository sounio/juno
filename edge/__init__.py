"""Edge Computing Engine - On-device model inference."""

from abc import ABC, abstractmethod
from typing import Any, Optional, AsyncIterator
from dataclasses import dataclass
from shared.config import settings


@dataclass
class ModelInfo:
    name: str
    provider: str
    path: str
    size: str
    quantization: Optional[str] = None
    is_loaded: bool = False


class EdgeProvider(ABC):
    @abstractmethod
    async def load_model(self, model_name: str) -> bool:
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def unload_model(self):
        pass

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        pass


class MLXProvider(EdgeProvider):
    """Apple MLX framework - optimized for Apple Silicon."""

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._current_model_name: Optional[str] = None

    async def load_model(self, model_name: str) -> bool:
        try:
            import mlx_lm
            self._model, self._tokenizer = mlx_lm.load(
                f"{settings.mlx_model_path}/{model_name}"
            )
            self._current_model_name = model_name
            return True
        except ImportError:
            return False
        except Exception:
            return False

    async def generate(self, prompt: str, **kwargs) -> str:
        if self._model is None:
            return "MLX model not loaded"
        import mlx_lm
        response = mlx_lm.generate(
            self._model, self._tokenizer, prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 2048),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        if self._model is None:
            yield "MLX model not loaded"
            return
        import mlx_lm
        for token in mlx_lm.stream_generate(
            self._model, self._tokenizer, prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 2048),
        ):
            yield token

    async def unload_model(self):
        self._model = None
        self._tokenizer = None
        self._current_model_name = None

    async def list_models(self) -> list[ModelInfo]:
        import os
        if not os.path.exists(settings.mlx_model_path):
            return []
        return [
            ModelInfo(name=d, provider="mlx", path=f"{settings.mlx_model_path}/{d}")
            for d in os.listdir(settings.mlx_model_path)
            if os.path.isdir(f"{settings.mlx_model_path}/{d}")
        ]


class OllamaProvider(EdgeProvider):
    """Ollama bridge for local LLMs."""

    def __init__(self):
        self._base_url = settings.ollama_base_url

    async def load_model(self, model_name: str) -> bool:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/pull",
                json={"name": model_name},
                timeout=300,
            )
            return resp.is_success

    async def generate(self, prompt: str, **kwargs) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": kwargs.get("model", settings.ollama_default_model),
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 2048),
                    },
                },
                timeout=120,
            )
            return resp.json().get("response", "")

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        import httpx
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json={
                    "model": kwargs.get("model", settings.ollama_default_model),
                    "prompt": prompt,
                    "stream": True,
                },
                timeout=120,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.strip():
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

    async def unload_model(self):
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self._base_url}/api/generate",
                json={"model": settings.ollama_default_model, "keep_alive": 0},
            )

    async def list_models(self) -> list[ModelInfo]:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/api/tags")
            if not resp.is_success:
                return []
            models = resp.json().get("models", [])
            return [
                ModelInfo(
                    name=m["name"],
                    provider="ollama",
                    path=m.get("model_path", ""),
                    size=m.get("size", ""),
                )
                for m in models
            ]


class EdgeEngine:
    def __init__(self):
        self.providers: dict[str, EdgeProvider] = {
            "mlx": MLXProvider(),
            "ollama": OllamaProvider(),
        }
        self._active_provider: Optional[str] = None

    async def auto_select(self) -> str:
        for name, provider in self.providers.items():
            models = await provider.list_models()
            if models:
                self._active_provider = name
                return name
        self._active_provider = "ollama"
        return "ollama"

    @property
    def active(self) -> Optional[EdgeProvider]:
        if self._active_provider:
            return self.providers.get(self._active_provider)
        return None
