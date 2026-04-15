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

Your job is to decide whether answering the user's query requires searching the campus
knowledge base. The knowledge base contains ONLY the following topics:
- Grading scale, GPA, academic standing, probation, suspension
- Academic calendar: semester dates, add/drop deadlines, registration windows
- Financial aid: FAFSA, scholarships, grants, loans, work-study, SAP
- Course catalog: course descriptions, prerequisites, credit load, Gen Ed requirements
- Registration: how to register, holds, waitlists, withdrawals, transcripts, graduation
- Student handbook: honor code, academic integrity, attendance, student rights, conduct
- Campus map and locations: buildings, office locations, room numbers, phone numbers, hours
- Dining and housing: residence halls, meal plans, dining locations, roommates, housing application
- IT services: WiFi, VPN, email, software, printing, MFA, student portal
- Library: hours, borrowing, databases, equipment lending, study rooms, research help
- Clubs and organizations: how to join/start clubs, SGA, intramural sports, volunteering

Answer "true" if the user's question could plausibly be answered by any of the topics above,
even if they do not use the exact words — judge by what they are ASKING FOR, not the words they use.

Examples that are "true":
- "when does the gym close?" → campus building hours
- "can I switch roommates?" → housing policy
- "I got a D, will I lose my scholarship?" → GPA + financial aid
- "where do I go to pay tuition?" → office locations
- "what happens if I miss too many classes?" → attendance policy

Answer "false" ONLY if the query is clearly outside all of the above topics:
- Casual greetings or small talk (hi, thanks, how are you)
- Current events, world news, weather, sports scores
- General knowledge with no campus angle (capital cities, historical facts, math problems)

When in doubt, answer "true".
            """),
            HumanMessage(content="{query}")
        ])
