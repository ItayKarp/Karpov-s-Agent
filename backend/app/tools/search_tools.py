from langchain_tavily import TavilySearch

import os
from app.core import settings


async def get_search_tools():
    os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
    tavily_tool = TavilySearch(max_results=5)
    return [tavily_tool,]