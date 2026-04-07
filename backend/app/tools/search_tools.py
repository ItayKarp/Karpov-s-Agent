from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

from app.core import settings


async def get_search_tools():
    wrapper = TavilySearchAPIWrapper(tavily_api_key=settings.tavily_api_key)
    tavily_tool = TavilySearchResults(max_results=5, api_wrapper=wrapper)
    return [tavily_tool,]