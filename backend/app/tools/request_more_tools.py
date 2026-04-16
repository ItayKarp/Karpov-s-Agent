import json
from langchain_core.tools import tool


@tool
async def request_more_tools(tool_names: list[str]):
    """
    Request additional tools that you don't currently have access to.
    Call this when you need a capability not available in your current toolset.
    Available tools you can request: tavily_search, fetch, search_papers, download_paper
    """
    return json.dumps(tool_names)