from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.base_class import BaseClass
from app.core.config import settings


class BasicAgent(BaseClass):
    def __init__(self, chat_repo):
        super().__init__(chat_repo=chat_repo)
        model = ChatOpenAI(model="gpt-5.4-nano",max_tokens=1000,timeout=30, api_key=settings.openai_api_key)
        self.llm = model
        self.system_prompt = ChatPromptTemplate.from_messages([
      ("system",
          """You are a helpful assistant. Answer the user's question clearly and concisely.
                                                                                                                                                                         
  What you know about this user:
  {memories}                                                                                                                                                             
  {context_section}

  You have been given a set of tools relevant to this query. Use them if needed.
  If you need a tool you don't currently have access to, call request_more_tools with the tool name.                                                                     
                                                                                                                                                                         
  Available tools you can request:                                                                                                                                       
  {tool_manifest}"""),
      MessagesPlaceholder(variable_name="messages")
  ])
