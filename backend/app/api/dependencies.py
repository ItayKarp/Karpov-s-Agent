from fastapi import Depends, Request
from app.agents.advanced_agent import AdvancedAgent
from app.agents.basic_agent import BasicAgent
from app.infrastructure.db.init_mongo import MongoManager
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.orchestrator.intent_classifier import IntentClassifier
from app.infrastructure.db.init_redis import RedisManager
from app.services.title_service import TitleService
from app.tools.registry import get_basic_tools, get_advanced_tools


async def get_chat_repo(
        mongo_client: MongoManager = Depends(MongoManager.get_db),
        redis_client: RedisManager = Depends(RedisManager.get_client)
):
    return ChatRepository(
        mongo_client=mongo_client,
        redis_client=redis_client
    )



async def get_title_service(chat_repo = Depends(get_chat_repo)):
    return TitleService(chat_repo=chat_repo, model = "gpt-5.4-nano")


async def get_agent_orchestrator(
        request: Request,
        mongo_client: MongoManager = Depends(MongoManager.get_db),
        redis_client: RedisManager = Depends(RedisManager.get_client),
        title_service: TitleService = Depends(get_title_service),
        chat_repo: ChatRepository = Depends(get_chat_repo)
):
    basic_tools = request.app.state.basic_tools
    advanced_tools = request.app.state.advanced_tools

    return AgentOrchestrator(
        intent_classifier=IntentClassifier(),

        chat_repo=chat_repo,

        advanced_agent= AdvancedAgent(
            chat_repo=chat_repo,
            tools=advanced_tools,
            title_service=title_service),

        basic_agent= BasicAgent(
            chat_repo=chat_repo,
            tools=basic_tools,
            title_service=title_service)
    )

