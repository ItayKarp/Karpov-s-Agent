from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings

class IntentClassifier:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-nano", api_key=settings.openai_api_key)

    async def classify(self, query: str) -> str:
        response = await self.llm.ainvoke([
            SystemMessage(content="""You are a routing classifier. Classify the user's message as either "basic" or "advanced".                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                         
  Route to "basic" if the query:                                                                                                                                                                                                                                                         
  - Requires only a web search to answer (current events, facts, prices, news, general knowledge)                                                                                                                                                                                        
  - Is a simple, single-step lookup question                                                                                                                                                                                                                                             
  - Examples: "What's the weather in Paris?", "Who won the 2024 election?", "What is the capital of Brazil?"                                                                                                                                                                             
                                                                                                                                                                                                                                                                                         
  Route to "advanced" if the query:                                                                                                                                                                                                                                                      
  - Requires actions beyond web search (file operations, email, calendar, code execution, data analysis)                                                                                                                                                                                 
  - Involves multi-step reasoning or planning across multiple tools                                                                                                                                                                                                                      
  - Needs to read, write, or interact with external services                                                                                                                                                                                                                             
  - Examples: "Schedule a meeting and send an invite", "Analyze this dataset and summarize it", "Draft and send an email about X"                                                                                                                                                        
                                                                                                                                                                                                                                                                                         
  Respond with only one word: basic or advanced."""),
            HumanMessage(content=query)
        ])
        return response.content.strip().lower()