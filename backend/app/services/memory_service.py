from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings

class MemoryService:
    def __init__(self,chat_repo, model, mem0_client):
        self.chat_repo = chat_repo
        self.mem0_client = mem0_client
        self.memory_llm = ChatOpenAI(model=model,max_tokens=100 ,timeout=10, api_key=settings.openai_api_key)
        self.extraction_prompt = """Your job is to extract long-term facts about the user from this conversation exchange.                                           
                  
  Save ONLY:                                                                                                                                              
  - Personal facts (name, age, location)
  - Their job, role, or expertise
  - Goals or projects they are working on                                                                                                                 
  - Explicit preferences ("I prefer", "I like", "I always use")
                                                                                                                                                          
  Do NOT save:    
  - Questions they asked                                                                                                                                  
  - Facts about the world or technology
  - Anything the assistant said
  - One-off requests unlikely to matter again                                                                                                             
   
  If nothing is worth saving, return exactly: NONE                                                                                                        
  Otherwise return one concise sentence starting with "User" """
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.extraction_prompt),
            HumanMessage(content="{query}"),
            AIMessage(content="{query}")
        ])

    async def process(self, query : str, ai_response: str, user_id: str):
        chain = self.prompt | self.memory_llm | StrOutputParser()
        result = await chain.ainvoke({"query":query, "ai_response": ai_response})
        fact = result.strip()
        if fact and fact.lower() != "none":
            return await self.chat_repo.save_memory(fact, user_id)
        return None