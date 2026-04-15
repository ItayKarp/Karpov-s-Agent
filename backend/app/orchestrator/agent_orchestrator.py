from time import time

from langchain_core.messages import HumanMessage
from starlette.responses import StreamingResponse

from app.models.schemas import AIQuerySchema

class AgentOrchestrator:
    def __init__(self, chat_repo, streaming_service):
        self.chat_repo = chat_repo
        self.streaming_service = streaming_service

    async def run(self, user_id: str, body: AIQuerySchema):
        chat_id = body.chat_id or await self.chat_repo.create_chat(user_id)

        initial_state = {
            "messages": [HumanMessage(content=body.prompt)],
            "user_id": user_id,
            "chat_id": chat_id
        }

        config = {
            "configurable": {
                "thread_id": chat_id,
                "start_time": time()
            }
        }

        return StreamingResponse(
            self.streaming_service.stream(initial_state, config, user_id, chat_id),
            media_type="text/event-stream",
            headers={"X_Chat_Id": str(chat_id)}
        )


