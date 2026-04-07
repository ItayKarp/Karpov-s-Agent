from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core import settings


class TitleService:
    def __init__(self, chat_repo, model):
        self.chat_repo = chat_repo
        self.title_llm = ChatOpenAI(model=model, max_tokens=250, timeout=30, api_key=settings.openai_api_key)

    async def handle_title(self, chat_id, user_id, query, full_response):
        if not await self.chat_repo.has_title(chat_id=chat_id, user_id=user_id):
            title_response = await self.title_llm.ainvoke(
                [HumanMessage(
                    content=f"Give this chat a short 3-5 word title based on these messages: {query} {full_response}")]
            )
            await self.chat_repo.save_title(chat_id, user_id, title_response.content.strip())