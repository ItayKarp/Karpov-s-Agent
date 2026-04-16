from app.agents.graph.state import AgentState

ROUTE_MAP = {
    "advanced": "advanced_agent",
    "basic": "basic_agent"
}

def route_to_agents(state: AgentState) -> str:
    return ROUTE_MAP.get(state["mode"], "basic_agent")


def should_continue_basic(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "basic_tools"
    return "finalize"


def should_continue_advanced(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "advanced_tools"
    return "finalize"