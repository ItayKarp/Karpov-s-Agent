from app.tools.search_tools import get_search_tools

async def get_basic_tools(mcp_client):
    all_mcp_tools = await mcp_client.get_tools()
    mem0_tools = [t for t in all_mcp_tools if "mem0" in t.name]
    return [
        *await get_search_tools(),
        *mem0_tools
    ]


async def get_advanced_tools(mcp_client):
    return [
        *await get_search_tools(),
        *await mcp_client.get_tools()
    ]