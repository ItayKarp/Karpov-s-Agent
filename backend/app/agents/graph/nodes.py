from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from time import time

from app.agents.graph.state import AgentState
import asyncio

class AgentNodes:
    def __init__(
            self,
            chat_repo,
            intent_classifier,
            vector_repository,
            basic_agent,
            advanced_agent,
            title_service,
            memory_service,
    ):
        self.chat_repo = chat_repo
        self.intent_classifier = intent_classifier
        self.vector_repository = vector_repository
        self.basic_agent = basic_agent
        self.advanced_agent = advanced_agent
        self.title_service = title_service
        self.memory_service = memory_service

    async def setup(self, state: AgentState) -> dict:
        user_id= state['user_id']
        chat_id = state['chat_id']
        prompt = state['messages'][-1].content
        (mode, needs_retrieval), memories = await asyncio.gather(
            self.intent_classifier.classify(prompt),
            self.chat_repo.get_relevant_memories(prompt, user_id))

        return {
            "chat_id": chat_id,
            "mode": mode,
            "needs_retrieval": needs_retrieval,
            "memories": memories
        }


    async def retrieve_docs_node(self, state: AgentState) -> dict:
        needs_retrieval = state['needs_retrieval']
        prompt = state['messages'][-1].content
        docs = await self.vector_repository.get_docs(needs_retrieval, prompt)
        return {
            "docs": docs
        }


    async def advanced_agent_node(self, state: AgentState) -> dict:
        response = await self.advanced_agent.execute(state)
        return {"messages": [AIMessage(content=response)]}


    async def basic_agent_node(self, state: AgentState):
        response = await self.basic_agent.execute(state)
        return {"messages": [AIMessage(content=response)]}

    async def finalize_node(self, state: AgentState, config: RunnableConfig) -> dict:
        start_time = config["configurable"]["start_time"]
        elapsed_time = round(time() - start_time, 1)

        prompt = state['messages'][-2].content
        response_text = state['messages'][-1].content
        user_id= state['user_id']
        chat_id = state['chat_id']

        await asyncio.gather(
            self.title_service.handle_title(chat_id, user_id, prompt, response_text),
            self.memory_service.process(query=prompt, ai_response=response_text, user_id=user_id)
        )

        return {"elapsed": elapsed_time}