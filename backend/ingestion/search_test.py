"""
Search test — query the Pinecone index and inspect the top results.

Usage:
    uv run python -m ingestion.search_test "what is the grading scale?"
    uv run python -m ingestion.search_test "wifi password" --k 5
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.core.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def search(query: str, k: int = 5) -> None:
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=settings.openai_api_key)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    results = vector_store.similarity_search_with_score(query, k=k)

    print(f"\nQuery: {query!r}")
    print(f"Top {len(results)} results:\n")
    print("─" * 80)

    for i, (doc, score) in enumerate(results, 1):
        meta = doc.metadata
        print(f"[{i}] Score: {score:.4f}")
        print(f"     Source : {meta.get('source', '?')}")
        print(f"     Topic  : {', '.join(meta.get('topic_tags', []))}")
        print(f"     Chunk  : {meta.get('chunk_index')} / {meta.get('total_chunks', '?') - 1}")
        print(f"     Text   : {doc.page_content[:300].strip()}...")
        print("─" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search the Pinecone index with a natural language query.")
    parser.add_argument("query", help="The search query.")
    parser.add_argument("--k", type=int, default=5, help="Number of results to return (default: 5).")
    args = parser.parse_args()

    search(query=args.query, k=args.k)
