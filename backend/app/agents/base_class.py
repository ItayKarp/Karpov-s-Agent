import json
from time import time
from langchain_core.messages import HumanMessage, AIMessage
import asyncio

class BaseClass:
    def __init__(self, chat_repo, title_service, memory_service):
        self.chat_repo = chat_repo
        self.memory_service = memory_service
        self.title_service = title_service
        self.dictionary_tools = {
            "tavily_search_results_json": lambda tool_input: f"Searching the web for {tool_input['query']}",
            "search_papers": lambda tool_input: f"Looking up academic papers on {tool_input['query']}",
            "fetch": lambda tool_input: f"Fetching content from {tool_input['url']}",
        }

    async def get_compatible_history(self, user_id, chat_id):
        raw_history = await self.chat_repo.get_five_messages(chat_id=chat_id, user_id=user_id)

        history_messages = []
        for msg in raw_history:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            else:
                history_messages.append(AIMessage(content=msg["content"]))

        return history_messages

    async def _stream(self, llm, system, chat_history, query, user_id, chat_id, start_time):
        full_response = ""
        root_run_id = None
        thoughts = []
        try:
            async for event in llm.astream_events({"messages": [system, *chat_history, HumanMessage(content=query)]}):
                kind = event["event"]

                if kind == "on_chain_start":
                    if not root_run_id:
                        root_run_id = event["run_id"]

                elif kind == "on_chat_model_start":
                    thoughts.append({"type": "thought", "content": "thinking..."})
                    yield json.dumps({"type": "thought", "content": "thinking..."}) + "\n"

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event["data"]["input"]
                    message = self.dictionary_tools.get(tool_name, lambda i: f"Using {tool_name}")(tool_input)
                    thoughts.append({"type": "thought", "content": message})
                    yield json.dumps({"type": "thought", "content": message}) + "\n"

                elif kind == "on_tool_end":
                    thoughts.append({"type": "thought", "content": f"Got results, processing..."})
                    yield json.dumps({"type": "thought", "content": f"Got results, processing..."}) + "\n"

                elif kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        full_response += chunk
                        yield json.dumps({"type": "token", "content": chunk}) + "\n"

                elif kind == "on_chain_end":
                    if event["run_id"] == root_run_id:
                        elapsed = round(time() - start_time, 1)
                        thoughts.append({"type": "end", "content": f"Thought for {elapsed} seconds"})
                        yield json.dumps({"type": "end", "content": f"Thought for {elapsed} seconds"}) + "\n"
                        await asyncio.gather(
                            self.chat_repo.save_message(role="assistant", message=full_response, user_id=user_id,
                                                        chat_id=chat_id, thoughts=thoughts),
                            self.title_service.handle_title(chat_id, user_id, query, full_response),
                            self.memory_service.process(query=query, ai_response=full_response, user_id=user_id)
                        )
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    @staticmethod
    def get_context_section(docs):
        context_section = ""
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
            context_section = f"\n\nRelevant campus information:\n{context}\n\n Use the information above to answer if relevant."

        return context_section