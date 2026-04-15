class VectorRepository:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def get_docs(self ,needs_retrieval, prompt):
        docs = []
        if needs_retrieval:
            results = await self.vector_store.asimilarity_search_with_score(prompt, k=4)
            print(f"DEBUG raw results: {[(score, doc.metadata.get('source')) for doc, score in results]}")
            docs = [doc for doc, score in results if score >= 0.35]

        return docs