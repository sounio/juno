"""
Multi-Agent Orchestrator (LangGraph)
=====================================
Central coordinator that routes requests to specialized agents.
"""

from typing import Annotated, Any, Literal, Optional
from typing_extensions import TypedDict
from dataclasses import dataclass, field
from enum import Enum


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    TASK = "task"
    DEVICE = "device"


class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    user_id: str
    device_id: str
    current_agent: AgentRole
    context: dict[str, Any]
    tool_calls: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass
class AgentCapability:
    name: str
    description: str
    tools: list[str]
    models: list[str] = field(default_factory=list)


class BaseAgent:
    def __init__(self, role: AgentRole, capabilities: list[AgentCapability]):
        self.role = role
        self.capabilities = capabilities

    async def process(self, state: AgentState) -> AgentState:
        raise NotImplementedError


class Orchestrator:
    def __init__(self):
        self.agents: dict[AgentRole, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.role] = agent

    async def route(self, state: AgentState) -> AgentState:
        message = state["messages"][-1]["content"] if state["messages"] else ""

        intent = self._classify_intent(message, state)

        target_role = self._resolve_agent(intent, state)
        state["current_agent"] = target_role

        # Orchestrator only routes — agent processing happens in LangGraph nodes
        state["metadata"]["routed_to"] = target_role.value
        return state

    def _classify_intent(self, message: str, state: AgentState) -> str:
        return "conversation"

    def _resolve_agent(self, intent: str, state: AgentState) -> AgentRole:
        return AgentRole.CONVERSATION


default_orchestrator = Orchestrator()


async def run_agent_loop(state: AgentState) -> AgentState:
    return await default_orchestrator.route(state)
