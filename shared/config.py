from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Juno"
    debug: bool = True

    # LLM Configuration
    llm_default_provider: str = "deepseek"
    llm_default_model: str = "deepseek-chat"
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    # Fallback providers
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None

    # Edge / Local Models
    mlx_model_path: str = "./data/models/mlx"
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "qwen2.5:7b"

    # Storage
    database_url: str = "sqlite+aiosqlite:///./data/assistant.db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_persist_dir: str = "./data/chroma"

    # MCP
    mcp_enable_stdio: bool = True
    mcp_enable_sse: bool = True
    mcp_max_tool_timeout: int = 120

    # Event Bus
    event_bus_provider: str = "redis"  # redis | local

    # Auth
    secret_key: str = "dev-secret-change-in-production"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
