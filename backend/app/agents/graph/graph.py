from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.types import RetryPolicy

from app.agents.graph.state import AgentState
from app.agents.graph.nodes import AgentNodes
from app.agents.graph.edges import route_to_agents, should_continue_basic, should_continue_advanced
from app.tools.request_more_tools import request_more_tools
from app.tools.tool_registry import get_all_tools

def create_graph(
        chat_repo,
        intent_classifier,
        vector_repository,
        basic_agent,
        advanced_agent,
        title_service,
        memory_service,
):
    nodes = AgentNodes(
        chat_repo=chat_repo,
        intent_classifier=intent_classifier,
        vector_repository=vector_repository,
        basic_agent=basic_agent,
        advanced_agent=advanced_agent,
        title_service=title_service,
        memory_service=memory_service,
    )

    basic_tool_node = ToolNode([*get_all_tools(), request_more_tools])
    advanced_tool_node = ToolNode([*get_all_tools(), request_more_tools])

    policy = RetryPolicy(max_attempts=3)

    builder = StateGraph(AgentState) # type: ignore

    builder.add_node("setup", nodes.setup, retry_policy=policy) # type: ignore
    builder.add_node("retrieve_docs", nodes.retrieve_docs_node, retry_policy=policy) # type: ignore
    builder.add_node("advanced_agent", nodes.advanced_agent_node, retry_policy=policy) # type: ignore
    builder.add_node("basic_agent", nodes.basic_agent_node, retry_policy=policy) # type: ignore
    builder.add_node("basic_tools", basic_tool_node, retry_policy=policy)
    builder.add_node("advanced_tools", advanced_tool_node, retry_policy=policy)
    builder.add_node("finalize", nodes.finalize_node, retry_policy=policy) # type: ignore

    builder.add_edge(START, "setup")
    builder.add_edge("setup", "retrieve_docs")
    builder.add_conditional_edges("retrieve_docs", route_to_agents, {
        "basic_agent": "basic_agent",
        "advanced_agent": "advanced_agent"
    })
    builder.add_conditional_edges("basic_agent", should_continue_basic, {
        "basic_tools": "basic_tools",
        "finalize": "finalize"
    })
    builder.add_conditional_edges("advanced_agent", should_continue_advanced, {
        "advanced_tools": "advanced_tools",
        "finalize": "finalize"
    })
    builder.add_edge("basic_tools", "basic_agent")
    builder.add_edge("advanced_tools", "advanced_agent")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=MemorySaver())