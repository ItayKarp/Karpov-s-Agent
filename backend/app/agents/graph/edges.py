from app.agents.graph.state import AgentState

ROUTE_MAP = {
    "advanced": "advanced_agent",
    "basic": "basic_agent"
}

def route_to_agents(state: AgentState) -> str:
    return ROUTE_MAP.get(state["mode"], "basic_agent")