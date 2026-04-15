from contextlib import asynccontextmanager
from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from app.core import settings
from app.infrastructure.db.init_mem0 import Mem0Manager
from app.infrastructure.db.init_mongo import MongoManager
from app.infrastructure.db.init_qdrant import QdrantManager
from app.infrastructure.db.init_redis import RedisManager
from app.core.mcp_config import get_mcp_config
from app.tools.search_tools import get_search_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    await QdrantManager.init()
    await MongoManager.init()
    await RedisManager.init()
    await Mem0Manager.init()
    client = MultiServerMCPClient(get_mcp_config())
    search_tools = await get_search_tools()

    async with (
        client.session("arxiv") as arxiv_session,
        client.session("fetch") as fetch_session,
    ):
        arxiv_tools = await load_mcp_tools(arxiv_session)
        fetch_tools = await load_mcp_tools(fetch_session)

        app.state.basic_tools = [*search_tools]
        app.state.advanced_tools = [*search_tools, *arxiv_tools, *fetch_tools]

        yield

    await MongoManager.close()
    await RedisManager.close()
    await QdrantManager.close()
