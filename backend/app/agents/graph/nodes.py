import json
import asyncio
from time import time
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import adispatch_custom_event
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from app.core import settings
from app.agents.graph.state import AgentState
from app.tools.tool_registry import get_tool_manifest


class ToolSelection(BaseModel):
    tool_names: list[str] = Field(description="Names of the tools needed to answer this query.")

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
        await adispatch_custom_event("thought", {"content" : "Setting up ..."})
        user_id= state['user_id']
        chat_id = state['chat_id']
        prompt = state['messages'][-1].content
        (mode, needs_retrieval), memories, tools = await asyncio.gather(
            self.intent_classifier.classify(prompt),
            self.chat_repo.get_relevant_memories(prompt, user_id),
            self.select_tools(prompt)
        )


        return {
            "chat_id": chat_id,
            "mode": mode,
            "needs_retrieval": needs_retrieval,
            "memories": memories,
            "selected_tools": tools
        }


    async def retrieve_docs_node(self, state: AgentState) -> dict:
        await adispatch_custom_event("thought", {"content" : "Retrieving docs ..."})
        needs_retrieval = state['needs_retrieval']
        prompt = state['messages'][-1].content
        docs = await self.vector_repository.get_docs(needs_retrieval, prompt)
        return {
            "docs": docs
        }


    async def advanced_agent_node(self, state: AgentState) -> dict:
        await adispatch_custom_event("thought", {"content" : "Thinking ..."})
        updated_state = {**state, "selected_tools": await self._get_updated_tools(state)}
        response = await self.advanced_agent.execute(updated_state)
        return {"messages": [response], "selected_tools": updated_state["selected_tools"]}


    async def basic_agent_node(self, state: AgentState):
        await adispatch_custom_event("thought", {"content" : "Thinking ..."})
        updated_state = {**state, "selected_tools": await self._get_updated_tools(state)}
        response = await self.basic_agent.execute(updated_state)
        return {"messages": [response], "selected_tools": updated_state["selected_tools"]}

    async def finalize_node(self, state: AgentState, config: RunnableConfig) -> dict:
        start_time = config["configurable"]["start_time"]
        elapsed_time = round(time() - start_time, 1)
        await adispatch_custom_event("thought", {"content" : f"Thought for {elapsed_time}s"})
        prompt = ""
        for message in reversed(state['messages']):
            if isinstance(message, HumanMessage):
                prompt = message.content
                break

        response_text = state['messages'][-1].content
        user_id= state['user_id']
        chat_id = state['chat_id']

        await asyncio.gather(
            self.title_service.handle_title(chat_id, user_id, prompt, response_text),
            self.memory_service.process(query=prompt, ai_response=response_text, user_id=user_id)
        )

        return {"elapsed": elapsed_time}


    @staticmethod
    async def select_tools(prompt) -> dict:
        manifest = get_tool_manifest()

        selector_llm = ChatOpenAI(
            model="gpt-5.4-nano",
            api_key=settings.openai_api_key
        ).with_structured_output(ToolSelection)

        result = await selector_llm.ainvoke([
            SystemMessage(content=f"""You are a tool selector. Given a user query, pick only the tools needed to answer it.
            Available tools:
            {manifest}
            
            Only select tools that are genuinely needed. If the query is conversational or factual from memory, select none."""),
            HumanMessage(content=prompt)
        ])
        return result.tool_names


    @staticmethod
    async def _get_updated_tools(state: AgentState):
        messages = state["messages"]

        for message in reversed(messages):
            if isinstance(message, ToolMessage) and message.name=="request_more_tools":
                parsed_message = json.loads(message.content)
                return list(set(state.get("selected_tools", []) + parsed_message))
        return state.get("selected_tools", [])
