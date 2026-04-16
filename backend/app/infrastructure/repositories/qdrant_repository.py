from langchain_openai import OpenAIEmbeddings

from app.core import settings


class QdrantRepository:
    def __init__(self, qdrant_client, embedding_model: str ):
        self.qdrant_client = qdrant_client
        self.embedder = OpenAIEmbeddings(
            model= embedding_model,
            openai_api_key=settings.openai_api_key
        )

    CAMPUS_KEYWORDS = {"campus", "university", "college", "school", "dining", "housing", "library", "registrar", "financial aid", "tuition", "dorm", "syllabus", "professor", "course", "gpa", "scholarship"}

    async def get_docs(self,needs_retrieval: bool, query:str, top_k: int = 3) -> list:
        keyword_match = any(kw in query.lower() for kw in self.CAMPUS_KEYWORDS)
        if needs_retrieval or keyword_match:
            vector = await self.embedder.aembed_query(query)

            results = await self.qdrant_client.query_points(
                collection_name=settings.qdrant_collection_name,
                query=vector,
                limit=top_k,
                with_payload=True,
            )
            docs = [doc.payload["text"] for doc in results.points if doc.score > 0.4]

            return docs
        else:
            return []