from app.agents.graph.state import AgentState


class BaseClass:
    def __init__(self,chat_repo):
        self.chat_repo = chat_repo
        self.system_prompt = None
        self.llm = None


    @staticmethod
    async def astream(llm, formatted):
        response = await llm.ainvoke(formatted)

        return response


    async def execute(self, state: AgentState):
        user_id = state["user_id"]
        chat_id = state["chat_id"]
        memories = state["memories"]
        docs = state["docs"]
        messages = state["messages"]
        prompt = state["messages"][-1].content

        await self.chat_repo.save_message(user_id=user_id, chat_id=chat_id, role="user", message=prompt)

        context_section = self.get_context_section(docs)

        formatted = self.system_prompt.invoke({
            "memories": memories,
            "context_section": context_section,
            "messages": messages
        })

        return await self.astream(llm=self.llm, formatted=formatted)


    @staticmethod
    def get_context_section(docs):
        context_section = ""
        if docs:
            context = "\n\n".join([doc for doc in docs])
            context_section = f"\n\nRelevant campus information:\n{context}\n\n Use the information above to answer if relevant."

        return context_section