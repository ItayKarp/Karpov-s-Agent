from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings


class BasicAgent(BaseClass):
    def __init__(self, chat_repo, tools):
        super().__init__(chat_repo=chat_repo)
        self.tools = tools
        model = ChatOpenAI(model="gpt-5.4-nano",max_tokens=1000,timeout=30, api_key=settings.openai_api_key)
        self.llm = model.bind_tools(tools=[*self.tools])
        self.system_prompt = ChatPromptTemplate.from_messages([
            ("system",
                    """You are a helpful assistant. Answer the user's question clearly and concisely.
                    What you know about this user:
                    {memories}
                    {context_section}"""),
            MessagesPlaceholder(variable_name="messages")
        ])
