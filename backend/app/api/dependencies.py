from fastapi import Depends

from app.agents.advanced_agent import AdvancedAgent
from app.agents.basic_agent import BasicAgent
from app.agents.graph.graph import create_graph
from app.core import settings
from app.infrastructure.db.init_qdrant import QdrantManager
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.qdrant_repository import QdrantRepository
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.services.intent_classifier_service import IntentClassifierService
from app.services.memory_service import MemoryService
from app.services.streaming_service import StreamingService
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

async def get_qdrant_repo():
    return QdrantRepository(qdrant_client=QdrantManager.get_client(), embedding_model=settings.qdrant_embedding_model)

async def get_graph(
        chat_repo=Depends(get_chat_repo),
        title_service: TitleService = Depends(get_title_service),
        memory_service: MemoryService = Depends(get_memory_service),
        qdrant_repo=Depends(get_qdrant_repo),
):
    return create_graph(
        chat_repo=chat_repo,
        title_service=title_service,
        vector_repository=qdrant_repo,
        basic_agent=BasicAgent(
            chat_repo=chat_repo,
        ),
        advanced_agent=AdvancedAgent(
            chat_repo=chat_repo,
        ),
        memory_service=memory_service,
        intent_classifier=IntentClassifierService()
    )


async def get_streaming_service(
        chat_repo=Depends(get_chat_repo),
        graph=Depends(get_graph)
):
    return StreamingService(chat_repo=chat_repo, graph=graph)

async def get_agent_orchestrator(
        chat_repo: ChatRepository = Depends(get_chat_repo),
        streaming_service: StreamingService = Depends(get_streaming_service),
):
    return AgentOrchestrator(
        chat_repo=chat_repo,
        streaming_service=streaming_service
    )

