from contextlib import asynccontextmanager
from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.infrastructure.db.init_mongo import MongoManager
from app.infrastructure.db.init_redis import RedisManager
from app.core.mcp_config import get_mcp_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoManager.init()
    await RedisManager.init()
    client = MultiServerMCPClient(get_mcp_config())
    app.state.mcp_client = client
    app.state.basic_tools = await client.get_tools()
    app.state.advanced_tools = await client.get_tools()

    yield

    await MongoManager.close()
    await RedisManager.close()