from contextlib import asynccontextmanager
from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from app.core import settings
from app.infrastructure.db.init_mem0 import Mem0Manager
from app.infrastructure.db.init_mongo import MongoManager
from app.infrastructure.db.init_redis import RedisManager
from app.core.mcp_config import get_mcp_config
from app.tools.search_tools import get_search_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
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
        app.state.vector_store = vector_store

        yield

    await MongoManager.close()
    await RedisManager.close()
