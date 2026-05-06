from core import BaseAgent, AgentRole, AgentState, AgentCapability
from mcp import MCPRegistry
from core.llm import get_llm


class ConversationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.CONVERSATION,
            capabilities=[
                AgentCapability(
                    name="chat",
                    description="General conversation and question answering",
                    tools=["web_search", "get_time"],
                ),
            ],
        )

    async def process(self, state: AgentState) -> AgentState:
        messages = state.get("messages", [])
        llm = get_llm()
        response = await llm.chat(messages)

        state["messages"].append({
            "role": "assistant",
            "content": response,
        })
        state["metadata"]["agent"] = "conversation"
        state["metadata"]["provider"] = llm.model
        state["metadata"]["response"] = response
        return state


class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.KNOWLEDGE,
            capabilities=[
                AgentCapability(
                    name="rag",
                    description="Retrieve and reason over personal knowledge base",
                    tools=["web_search", "read_file"],
                ),
            ],
        )

    async def process(self, state: AgentState) -> AgentState:
        state["metadata"]["agent"] = "knowledge"
        return state


class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.TASK,
            capabilities=[
                AgentCapability(
                    name="automation",
                    description="Execute automated tasks and workflows",
                    tools=["run_shell", "list_directory", "read_file"],
                ),
            ],
        )

    async def process(self, state: AgentState) -> AgentState:
        state["metadata"]["agent"] = "task"
        return state


class DeviceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.DEVICE,
            capabilities=[
                AgentCapability(
                    name="device_sync",
                    description="Coordinate state across devices",
                    tools=[],
                ),
            ],
        )

    async def process(self, state: AgentState) -> AgentState:
        state["metadata"]["agent"] = "device"
        return state
