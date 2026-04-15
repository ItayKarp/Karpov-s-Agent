from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    chat_id: str
    mode: str
    needs_retrieval: bool
    memories: list
    docs: list
    elapsed: Optional[float]