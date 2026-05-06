"""Built-in MCP tool implementations."""

from mcp import MCPRegistry, MCPToolSchema
from shared.config import settings


@MCPRegistry.register("web_search", MCPToolSchema(
    name="web_search",
    description="Search the web for information",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "count": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
))
async def web_search(args: dict):
    import httpx
    query = args["query"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
        )
        return resp.text


@MCPRegistry.register("read_file", MCPToolSchema(
    name="read_file",
    description="Read contents of a file",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"},
        },
        "required": ["path"],
    },
))
def read_file(args: dict):
    with open(args["path"], "r") as f:
        return f.read()


@MCPRegistry.register("list_directory", MCPToolSchema(
    name="list_directory",
    description="List contents of a directory",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path"},
        },
        "required": ["path"],
    },
))
def list_directory(args: dict):
    import os
    return os.listdir(args["path"])


@MCPRegistry.register("run_shell", MCPToolSchema(
    name="run_shell",
    description="Execute a shell command (with user approval)",
    input_schema={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command"},
        },
        "required": ["command"],
    },
))
async def run_shell(args: dict):
    import asyncio
    proc = await asyncio.create_subprocess_shell(
        args["command"],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {"stdout": stdout.decode(), "stderr": stderr.decode(), "returncode": proc.returncode}


@MCPRegistry.register("get_time", MCPToolSchema(
    name="get_time",
    description="Get current date and time",
    input_schema={
        "type": "object",
        "properties": {
            "timezone": {"type": "string", "default": "UTC"},
        },
    },
))
def get_time(args: dict):
    from datetime import datetime, timezone
    return {"now": datetime.now(timezone.utc).isoformat()}
