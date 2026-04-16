import asyncio
from app.infrastructure.db.init_mongo import MongoManager
from app.infrastructure.db.init_redis import RedisManager
from app.infrastructure.db.init_qdrant import QdrantManager
from app.infrastructure.db.init_mem0 import Mem0Manager
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.qdrant_repository import QdrantRepository
from app.agents.basic_agent import BasicAgent
from app.agents.advanced_agent import AdvancedAgent
from app.services.intent_classifier_service import IntentClassifierService
from app.services.title_service import TitleService
from app.services.memory_service import MemoryService
from app.tools.search_tools import get_search_tools
from app.agents.graph.graph import create_graph
from app.core.config import settings


async def _init():
    # 1. Boot up all the databases
    await MongoManager.init()
    await RedisManager.init()
    await QdrantManager.init()
    await Mem0Manager.init()

    # 2. Get tools (skipping MCP for now)
    search_tools = await get_search_tools()

    # 3. Build all the dependencies (same as get_graph in dependencies.py)
    mongo_db = MongoManager.get_db()
    redis_client = RedisManager.get_client()
    mem0_client = await Mem0Manager.get_client()

    chat_repo = ChatRepository(mongo_client=mongo_db, redis_client=redis_client, mem0_client=mem0_client)
    qdrant_repo = QdrantRepository(qdrant_client=QdrantManager.get_client(),
                                   embedding_model=settings.qdrant_embedding_model)

    # 4. Build the graph with all real deps
    return create_graph(
        chat_repo=chat_repo,
        intent_classifier=IntentClassifierService(),
        vector_repository=qdrant_repo,
        basic_agent=BasicAgent(chat_repo=chat_repo, tools=search_tools),
        advanced_agent=AdvancedAgent(chat_repo=chat_repo, tools=search_tools),
        title_service=TitleService(chat_repo=chat_repo, model="gpt-5.4-nano"),
        memory_service=MemoryService(chat_repo=chat_repo, model="gpt-5.4-nano", mem0_client=mem0_client),
        basic_tools=search_tools,
        advanced_tools=search_tools
    )


graph = asyncio.run(_init())