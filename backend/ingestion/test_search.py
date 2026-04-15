"""
test_search.py — Interactive similarity search against the ingested Qdrant collection.

Usage:
    python -m ingestion.test_search
"""

from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from ingestion.config import settings, EMBEDDING_MODEL, QDRANT_COLLECTION_NAME

_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key or None,
    timeout=30,
)

_embedder = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    openai_api_key=settings.openai_api_key,
)


def search(query: str, top_k: int = 3) -> None:
    print(f"\nQuery: {query!r}")
    print("─" * 60)

    vector = _embedder.embed_query(query)

    results = _client.query_points(  # noqa: type-ignore — list[float] is valid per qdrant_client docs
        collection_name=QDRANT_COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload=True,
    ).points

    for i, point in enumerate(results, start=1):
        p = point.payload
        print(f"\n[{i}] {p['filename']}  (page {p['page']}, chunk {p['chunk_index']})  score={point.score:.4f}")
        print(f"    {p['text'][:300].strip()}")
        if len(p['text']) > 300:
            print("    …")

    print()


if __name__ == "__main__":
    queries = [
        "When does the fall semester start?",
        "How do I apply for financial aid?",
        "What dining options are available on campus?",
        "How do I register for classes?",
        "What clubs can I join?",
    ]

    for q in queries:
        search(q, top_k=3)
