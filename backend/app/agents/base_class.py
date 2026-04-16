from app.agents.graph.state import AgentState
from app.tools.request_more_tools import request_more_tools
from app.tools.tool_registry import get_tools, get_tool_manifest

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
        selected_tool_names = state.get("selected_tools", [])
        tools = get_tools(selected_tool_names)
        llm = self.llm.bind_tools([*tools, request_more_tools])

        await self.chat_repo.save_message(user_id=user_id, chat_id=chat_id, role="user", message=prompt)

        context_section = self.get_context_section(docs)

        tool_manifest = get_tool_manifest()

        formatted = self.system_prompt.invoke({
            "memories": memories,
            "context_section": context_section,
            "messages": messages,
            "tool_manifest": tool_manifest
        })

        return await self.astream(llm=llm, formatted=formatted)


    @staticmethod
    def get_context_section(docs):
        context_section = ""
        if docs:
            context = "\n\n".join([doc for doc in docs])
            context_section = f"\n\nRelevant campus information:\n{context}\n\n Use the information above to answer if relevant."

        return context_section