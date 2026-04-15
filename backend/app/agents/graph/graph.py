from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.graph.state import AgentState
from app.agents.graph.nodes import AgentNodes
from app.agents.graph.edges import route_to_agents

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

    builder = StateGraph(AgentState) # type: ignore

    builder.add_node("setup", nodes.setup) # type: ignore
    builder.add_node("retrieve_docs", nodes.retrieve_docs_node) # type: ignore
    builder.add_node("advanced_agent", nodes.advanced_agent_node) # type: ignore
    builder.add_node("basic_agent", nodes.basic_agent_node) # type: ignore
    builder.add_node("finalize", nodes.finalize_node) # type: ignore

    builder.add_edge(START, "setup")
    builder.add_edge("setup", "retrieve_docs")
    builder.add_conditional_edges("retrieve_docs", route_to_agents)
    builder.add_edge("basic_agent", "finalize")
    builder.add_edge("advanced_agent", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=MemorySaver())