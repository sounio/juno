"""Multi-Agent LangGraph workflow definition."""

from typing import Literal
from langgraph.graph import StateGraph, END
from core import AgentState, AgentRole
from core.agents import ConversationAgent, KnowledgeAgent, TaskAgent, DeviceAgent
from core import default_orchestrator

# register agents
default_orchestrator.register_agent(ConversationAgent())
default_orchestrator.register_agent(KnowledgeAgent())
default_orchestrator.register_agent(TaskAgent())
default_orchestrator.register_agent(DeviceAgent())


def route_agent(state: AgentState) -> Literal["conversation", "knowledge", "task", "device", "__end__"]:
    role = state.get("current_agent", AgentRole.CONVERSATION)
    return role.value


async def run_orchestrator(state: AgentState) -> AgentState:
    return await default_orchestrator.route(state)


async def run_conversation(state: AgentState) -> AgentState:
    agent = default_orchestrator.agents[AgentRole.CONVERSATION]
    return await agent.process(state)


async def run_knowledge(state: AgentState) -> AgentState:
    agent = default_orchestrator.agents[AgentRole.KNOWLEDGE]
    return await agent.process(state)


async def run_task(state: AgentState) -> AgentState:
    agent = default_orchestrator.agents[AgentRole.TASK]
    return await agent.process(state)


async def run_device(state: AgentState) -> AgentState:
    agent = default_orchestrator.agents[AgentRole.DEVICE]
    return await agent.process(state)


workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", run_orchestrator)
workflow.add_node("conversation", run_conversation)
workflow.add_node("knowledge", run_knowledge)
workflow.add_node("task", run_task)
workflow.add_node("device", run_device)

workflow.set_entry_point("orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    route_agent,
    {
        "conversation": "conversation",
        "knowledge": "knowledge",
        "task": "task",
        "device": "device",
        "__end__": END,
    },
)

for node in ["conversation", "knowledge", "task", "device"]:
    workflow.add_edge(node, END)

graph = workflow.compile()
