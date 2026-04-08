from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings
import asyncio

class AdvancedAgent(BaseClass):
    def __init__(self, tools, chat_repo, title_service, memory_service):
        super().__init__(chat_repo, title_service=title_service, memory_service=memory_service)
        self.tools = tools
        model = ChatOpenAI(model="gpt-5.4", max_tokens=3000, timeout=60, api_key=settings.openai_api_key)
        self.llm = create_agent(model=model, tools=[*tools])

    async def execute(self, query: str, user_id, chat_id, memories, start_time):
        chat_history, _ = await asyncio.gather(
            self.get_compatible_history(chat_id=chat_id, user_id=user_id),
            self.chat_repo.save_message(user_id=user_id, chat_id=chat_id, role="user", message=query)
        )

        system = SystemMessage(
            content=f"You are an advanced AI assistant. You are professional, precise, and thorough in your responses. "
                    f"You have access to tools for searching the web, fetching content, and searching academic papers — use them when needed to provide accurate and up-to-date information. "
                    f"What you know about this user:"
                    f"{memories}"
                    f"Answer clearly and concisely."
        )

        async for chunk in self._stream(llm=self.llm, system=system, chat_history=chat_history, query=query, user_id=user_id, chat_id=chat_id, start_time=start_time):
            yield chunk
