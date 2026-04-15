from typing import Callable, Dict, AsyncGenerator
from time import time

from starlette.responses import StreamingResponse
import asyncio

from app.models.schemas import AIQuerySchema

class AgentOrchestrator:
    def __init__(self, intent_classifier, chat_repo, advanced_agent, basic_agent, qdrant_repo):
        self.intent_classifier = intent_classifier
        self.chat_repo = chat_repo
        self.advanced_agent = advanced_agent
        self.basic_agent = basic_agent
        self.qdrant_repo = qdrant_repo

        self.modes: Dict[str, Callable[..., AsyncGenerator[str, None]]] = {
            "advanced": self.advanced_agent.execute,
            "basic": self.basic_agent.execute
        }


    async def run(self, user_id: str, body: AIQuerySchema):
        start_time = time()
        if body.chat_id:
            (mode, needs_retrieval), memories = await asyncio.gather(
                self.intent_classifier.classify(body.prompt),
                self.chat_repo.get_relevant_memories(body.prompt, user_id),
            )
            chat_id = body.chat_id
        else:
            chat_id, (mode, needs_retrieval), memories = await asyncio.gather(
                self.chat_repo.create_chat(user_id),
                self.intent_classifier.classify(body.prompt),
                self.chat_repo.get_relevant_memories(body.prompt, user_id),
            )

        docs = await self.qdrant_repo.get_docs(needs_retrieval, prompt=body.prompt)



        stream = self.modes.get(mode)(body.prompt, user_id, chat_id, memories, docs, start_time)

        return StreamingResponse(stream, media_type="text/event-stream", headers={"X_Chat_Id": str(chat_id)})

