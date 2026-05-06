"""API Gateway - FastAPI with WebSocket support."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.config import settings
from mcp import MCPRegistry, MCPServer
import mcp.tools.builtin
from core.agents.workflow import graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    tools = MCPRegistry.list_tools()  # ensure tools are registered
    app.state.mcp_server = MCPServer()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "name": settings.app_name}


@app.get("/mcp/tools")
async def list_tools():
    return MCPRegistry.list_tools()


@app.post("/mcp/tools/{name}/execute")
async def execute_tool(name: str, args: dict):
    result = await MCPRegistry.execute(name, args)
    return {"result": result}


@app.post("/agent/chat")
async def agent_chat(payload: dict):
    messages = payload.get("messages", [])
    user_id = payload.get("user_id", "anonymous")
    device_id = payload.get("device_id", "web")

    state = {
        "messages": messages,
        "user_id": user_id,
        "device_id": device_id,
        "current_agent": "conversation",
        "context": {},
        "tool_calls": [],
        "metadata": {},
    }

    result = await graph.ainvoke(state)
    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "message":
                state = {
                    "messages": data.get("messages", []),
                    "user_id": data.get("user_id", "anonymous"),
                    "device_id": data.get("device_id", "web"),
                    "current_agent": "conversation",
                    "context": {},
                    "tool_calls": [],
                    "metadata": {},
                }
                result = await graph.ainvoke(state)
                await websocket.send_json({"type": "response", "data": result})

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
