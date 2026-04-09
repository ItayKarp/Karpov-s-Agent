from typing import Callable, Dict, AsyncGenerator
from time import time

from starlette.responses import StreamingResponse
import asyncio

from app.models.schemas import AIQuerySchema

class AgentOrchestrator:
    def __init__(self, intent_classifier, chat_repo, advanced_agent, basic_agent, vector_store):
        self.intent_classifier = intent_classifier
        self.chat_repo = chat_repo
        self.advanced_agent = advanced_agent
        self.basic_agent = basic_agent
        self.vector_store = vector_store

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

        docs = await self.get_docs(needs_retrieval, prompt=body.prompt)

        modes: Dict[str, Callable[..., AsyncGenerator[str, None]]] = {
            "advanced" : self.advanced_agent.execute,
            "basic" : self.basic_agent.execute
        }

        stream = modes.get(mode)(body.prompt, user_id, chat_id, memories, docs, start_time)

        return StreamingResponse(stream, media_type="text/event-stream", headers={"X_Chat_Id": str(chat_id)})

    async def get_docs(self ,needs_retrieval, prompt):
        docs = []
        if needs_retrieval:
            results = await self.vector_store.asimilarity_search_with_score(prompt, k=7)
            docs = [doc for doc, score in results if score >= 0.7]

        return docs
