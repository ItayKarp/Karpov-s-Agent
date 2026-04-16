from typing import Annotated, Optional, NotRequired
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

def merge_selected_tools(current: list, update: list) -> list:
    return list(set(current) | set(update))

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    chat_id: str
    selected_tools: NotRequired[Annotated[list, merge_selected_tools]]
    mode: NotRequired[str]
    needs_retrieval: NotRequired[bool]
    memories: NotRequired[list]
    docs: NotRequired[list]
    elapsed: NotRequired[Optional[float]]
