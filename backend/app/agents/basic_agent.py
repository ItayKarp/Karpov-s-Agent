from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings


class BasicAgent(BaseClass):
    def __init__(self, chat_repo, tools, title_service, memory_service):
        super().__init__(chat_repo, title_service=title_service, memory_service=memory_service)
        self.tools = tools
        model = ChatOpenAI(model="gpt-5.4-nano",max_tokens=1000,timeout=30, api_key=settings.openai_api_key)
        self.llm = create_agent(model=model, tools=[*self.tools], )


    async def execute(self, query: str, user_id, chat_id, memories, docs, start_time):
        chat_history = await self.get_compatible_history(user_id,chat_id)
        await self.chat_repo.save_message(user_id=user_id, chat_id=chat_id, role="user", message=query)

        context_section = self.get_context_section(docs)

        system = SystemMessage(
            content=f"You are a helpful assistant. Answer the user's question clearly and concisely. "
                    f"What you know about this user:"
                    f"{memories}"
                    f"{context_section}"
        )

        async for chunk in self._stream(llm=self.llm, system=system, chat_history=chat_history, query=query, user_id=user_id, chat_id=chat_id, start_time=start_time):
            yield chunk


