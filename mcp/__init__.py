from __future__ import annotations
import json
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel


class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


class MCPToolSchema(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = {"type": "object", "properties": {}}
    output_schema: dict[str, Any] = {"type": "object", "properties": {}}


class MCPResourceSchema(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


MCPToolHandler = Callable[[dict[str, Any]], dict[str, Any] | str]


@dataclass
class MCPToolRegistration:
    schema: MCPToolSchema
    handler: MCPToolHandler
    provider: str = "builtin"


class MCPRegistry:
    _tools: dict[str, MCPToolRegistration] = {}

    @classmethod
    def register(cls, name: str, schema: MCPToolSchema, handler: MCPToolHandler = None, provider: str = "builtin"):
        if handler is not None:
            cls._tools[name] = MCPToolRegistration(schema=schema, handler=handler, provider=provider)
            return handler

        def decorator(fn: MCPToolHandler):
            cls._tools[name] = MCPToolRegistration(schema=schema, handler=fn, provider=provider)
            return fn

        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[MCPToolRegistration]:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[MCPToolSchema]:
        return [reg.schema for reg in cls._tools.values()]

    @classmethod
    async def execute(cls, name: str, args: dict[str, Any]) -> Any:
        reg = cls.get(name)
        if not reg:
            raise ValueError(f"Tool '{name}' not found")
        if asyncio.iscoroutinefunction(reg.handler):
            return await reg.handler(args)
        return reg.handler(args)


class MCPServer:
    def __init__(self, name: str = "vela-mcp"):
        self.name = name
        self.registry = MCPRegistry
