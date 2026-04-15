from fastapi import Depends, Request
from app.agents.advanced_agent import AdvancedAgent
from app.agents.basic_agent import BasicAgent
from app.infrastructure.db.init_qdrant import QdrantManager
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.qdrant_repository import QdrantRepository
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.services.intent_classifier_service import IntentClassifierService
from app.services.memory_service import MemoryService
from app.services.title_service import TitleService
from app.infrastructure.db import MongoManager, RedisManager, Mem0Manager



async def get_chat_repo(
        mongo_client: MongoManager = Depends(MongoManager.get_db),
        redis_client: RedisManager = Depends(RedisManager.get_client),
        mem0_client: Mem0Manager = Depends(Mem0Manager.get_client)
):
    return ChatRepository(
        mongo_client=mongo_client,
        redis_client=redis_client,
        mem0_client=mem0_client
    )



async def get_title_service(chat_repo = Depends(get_chat_repo)):
    return TitleService(chat_repo=chat_repo, model = "gpt-5.4-nano")

async def get_memory_service(chat_repo = Depends(get_chat_repo), mem0_client = Depends(Mem0Manager.get_client)):
    return MemoryService(chat_repo=chat_repo, model = "gpt-5.4-nano", mem0_client=mem0_client)

async def get_agent_orchestrator(
        request: Request,
        title_service: TitleService = Depends(get_title_service),
        chat_repo: ChatRepository = Depends(get_chat_repo),
        memory_service: MemoryService = Depends(get_memory_service)
):
    basic_tools = request.app.state.basic_tools
    advanced_tools = request.app.state.advanced_tools
    vector_store = request.app.state.vector_store

    return AgentOrchestrator(
        intent_classifier=IntentClassifierService(),
        chat_repo=chat_repo,
        qdrant_repo= QdrantRepository(
            qdrant_client=QdrantManager.get_client(),
            embedding_model= "text-embedding-3-small"
        ),
        advanced_agent= AdvancedAgent(
            chat_repo=chat_repo,
            tools=advanced_tools,
            title_service=title_service,
            memory_service=memory_service,
        ),
        basic_agent= BasicAgent(
            chat_repo=chat_repo,
            tools=basic_tools,
            title_service=title_service,
            memory_service=memory_service
        )
    )

