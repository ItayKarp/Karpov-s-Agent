from typing import cast
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.models.schemas import IntentClassifierSchema, RetrievalRouterSchema


class IntentClassifierService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-nano", api_key=settings.openai_api_key)

    async def classify(self, query: str) -> tuple[str, bool]:
        intent_classify_chain = self.get_intent_prompt() | self.llm.with_structured_output(IntentClassifierSchema)
        needs_retrieval_chain = self.get_retrieval_prompt() | self.llm.with_structured_output(RetrievalRouterSchema)

        parallel_chain = RunnableParallel({
            "intent": intent_classify_chain,
            "needs_retrieval": needs_retrieval_chain
        })

        result = await parallel_chain.ainvoke({"query": query})

        intent = cast(IntentClassifierSchema, result["intent"])
        needs_retrieval = cast(RetrievalRouterSchema, result["needs_retrieval"])
        return intent.mode, needs_retrieval.content


    @staticmethod
    def get_intent_prompt():
        return ChatPromptTemplate.from_messages([
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
            HumanMessage(content="{query}")
        ])

    @staticmethod
    def get_retrieval_prompt():
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a retrieval routing classifier for a university campus assistant.                       
                                                                                                                                                                                                                                                                                                                         
            Your job is to decide whether answering the user's query requires searching the campus knowledge base (vector database containing campus-specific information such as courses, departments, staff, facilities, policies, events, schedules, and procedures).                                                           
                                                                                                                                                                                                                                                                                                                                 
            Answer "true" if the query:                                                                                                                                                                                                                                                                                            
            - Asks about anything specific to this university (courses, professors, departments, buildings, campus services, academic policies, enrollment, deadlines, student resources)                                                                                                                                          
            - Requires internal campus data that cannot be found via a general web search                                                                                                                                                                                                                                          
            - References campus entities by name (e.g. a department, a specific course code, a campus office)                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                 
            Answer "false" if the query:                                                                                                                                                                                                                                                                                           
            - Is general knowledge or current events unrelated to this campus                                                                                                                                                                                                                                                      
            - Can be answered without any campus-specific context                                                                                                                                                                                                                                                                  
            - Is a casual conversational message (greetings, thanks, etc.)                                                                                                                                                                                                                                                         
            - Requires only computation, reasoning, or action (no campus facts needed)                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                                                 
            Respond with only one word: true or false.
            """),
            HumanMessage(content="{query}")
        ])
