from typing import Callable, Dict

from starlette.responses import StreamingResponse

from app.models.schemas import AIQuerySchema

class AgentOrchestrator:
    def __init__(self, intent_classifier, chat_repo, advanced_agent, basic_agent):
        self.intent_classifier = intent_classifier
        self.chat_repo = chat_repo
        self.advanced_agent = advanced_agent
        self.basic_agent = basic_agent

    async def run(self, user_id: str, body: AIQuerySchema):

        chat_id = await self.chat_repo.create_chat(user_id) if not body.chat_id else body.chat_id

        mode = await self.intent_classifier.classify(body.prompt)

        modes: Dict[str, Callable] = {
            "advanced" : self.advanced_agent.execute,
            "basic" : self.basic_agent.execute
        }

        stream = modes.get(mode)(body.prompt, user_id, chat_id)

        return StreamingResponse(stream, media_type="text/event-stream", headers={"X_Chat_Id": str(chat_id)})