from typing import Annotated, Optional, NotRequired
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    chat_id: str
    mode: NotRequired[str]
    needs_retrieval: NotRequired[bool]
    memories: NotRequired[list]
    docs: NotRequired[list]
    elapsed: NotRequired[Optional[float]]