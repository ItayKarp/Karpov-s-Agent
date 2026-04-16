from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings

class AdvancedAgent(BaseClass):
    def __init__(self, chat_repo, tools):
        super().__init__(chat_repo=chat_repo)
        self.tools = tools
        model = ChatOpenAI(model="gpt-5.4", max_tokens=3000, timeout=60, api_key=settings.openai_api_key)
        self.llm = model.bind_tools(tools=[*tools])
        self.system_prompt = ChatPromptTemplate.from_messages([
            ("system",
                    """You are an advanced AI assistant. You are professional, precise, and thorough in your responses. 
                    You have access to tools for searching the web, fetching content, and searching academic papers — use them when needed to provide accurate and up-to-date information. 
                    What you know about this user:
                    {memories}
                    {context_section}
                    Answer clearly and concisely."""
        ),
            MessagesPlaceholder(variable_name="messages")
        ])

