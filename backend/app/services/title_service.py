from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core import settings


class TitleService:
    def __init__(self, chat_repo, model):
        self.chat_repo = chat_repo
        self.title_llm = ChatOpenAI(model=model, max_tokens=250, timeout=30, api_key=settings.openai_api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Generate a short 3-5 word title for a chat conversation.                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                         
  Rules:          
  - Maximum 5 words                                                                                                                                                                                                                                                                                                      
  - No punctuation or quotes
  - Capture the core topic only                                                                                                                                                                                                                                                                                          
  - Return only the title, nothing else"""),
            HumanMessage(content="{query}"),
            AIMessage(content="{response}")
        ])

    async def handle_title(self, chat_id, user_id, query, full_response):
        if not await self.chat_repo.has_title(chat_id=chat_id, user_id=user_id):
            chain = self.prompt | self.title_llm | StrOutputParser()
            title_response = await chain.ainvoke({"query": query, "response": full_response})
            await self.chat_repo.save_title(chat_id, user_id, title_response.strip())