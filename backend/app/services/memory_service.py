from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
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

    async def process(self, user_message:str, ai_response: str, user_id: str):
        result = await self.memory_llm.ainvoke([
            SystemMessage(content=self.extraction_prompt),
            HumanMessage(content=user_message),
            AIMessage(content=ai_response)
        ])
        fact = str(result.content).strip()
        if fact and fact != "NONE":
            return await self.chat_repo.save_memory(fact, user_id)
        return None