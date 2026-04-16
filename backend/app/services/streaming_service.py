import json


class StreamingService:
    def __init__(self, chat_repo, graph):
        self.chat_repo = chat_repo
        self.graph = graph

    async def stream(self, state, config, user_id, chat_id):
        full_response = ""
        thoughts = []

        async for event in self.graph.astream_events(state, config=config, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_stream":
                node = event.get("metadata", {}).get("langgraph_node", "")
                if node not in ("basic_agent", "advanced_agent"):
                    continue
                chunk = event["data"]["chunk"].content
                if chunk:
                    full_response += chunk
                    yield json.dumps({"type": "token", "content": chunk}) + "\n"

            elif kind == "on_tool_start":
                tool_input= event["data"].get("input", {})
                message = f"Searching for {tool_input}"
                thoughts.append({"type": "thought", "content": message})
                yield json.dumps({"type": "thought", "content": message}) + "\n"

            elif kind == "on_tool_end":
                thoughts.append({"type": "thought", "content": "Got results, processing..."})
                yield json.dumps({"type": "thought", "content": "Got results, processing..."}) + "\n"

            elif kind == "on_custom_event" and event["name"] == "thought":
                message = event["data"]["content"]
                thoughts.append({"type": "thought", "content": message})
                yield json.dumps({"type": "thought", "content": message}) + "\n"

        await self.chat_repo.save_message(
            role="assistant",
            message=full_response,
            user_id=user_id,
            chat_id=chat_id,
            thoughts=thoughts
        )