from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings


class BasicAgent(BaseClass):
    def __init__(self, chat_repo, tools, title_service):
        super().__init__(chat_repo, title_service=title_service)
        self.tools = tools
        model = ChatOpenAI(model="gpt-5.4-nano",max_tokens=1000,timeout=30, api_key=settings.openai_api_key)
        self.llm = create_agent(model=model, tools=[*self.tools], )


    async def execute(self, query: str, user_id, chat_id):
        chat_history = await self.get_compatible_history(user_id,chat_id)
        await self.chat_repo.save_message(user_id=user_id, chat_id=chat_id, role="user", message=query)

        system = SystemMessage(
            content=f"You are a helpful assistant. Answer the user's question clearly and concisely. "
                    f"MEMORY INSTRUCTIONS: "
                    f"1. Before responding, search your memory using keywords from the user's message to retrieve relevant context about this user. "
                    f"2. Save to memory only: user preferences, stated goals, personal facts the user explicitly shares, and recurring topics. "
                    f"3. Do NOT save: sensitive data, passwords, financial details, or one-off information unlikely to be relevant again. "
                    f"4. Before saving, check if a similar memory already exists to avoid duplicates. "
                    f"5. Always use memories to personalize your response when relevant. "
                    f"6. Always use '{user_id}' as the user_id parameter when calling any memory tool (search-memories, add-memory)."
                    f"You are currently assisting user {user_id}.")

        async for chunk in self._stream(llm=self.llm, system=system, chat_history=chat_history, query=query, user_id=user_id, chat_id=chat_id):
            yield chunk


