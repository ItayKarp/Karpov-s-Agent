from langchain_core.tools import tool
from langgraph.types import Command

@tool
async def request_more_tools(tool_names: list[str]) -> Command:
    """
    Request additional tools that you don't currently have access to.
    Call this when you need a capability not available in your current toolset.
    Available tools you can request: tavily_search, fetch, search_papers, download_paper
    """
    return Command(update={"selected_tools": tool_names})