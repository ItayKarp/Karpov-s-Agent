"""
Embedder — generates embeddings and upserts chunks into Pinecone.

Uses the same model and index as the application (text-embedding-3-small + langchain-pinecone)
so that query-time and ingestion-time embeddings are always consistent.
"""

import sys
import os

# Allow running from the backend/ root: python -m ingestion.pipeline
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone

from app.core.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def _build_vector_store() -> PineconeVectorStore:
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=settings.openai_api_key,
    )
    return PineconeVectorStore(index=index, embedding=embeddings)


def _chunks_to_documents(chunks: list[dict]) -> list[Document]:
    """Converts our chunk dicts into LangChain Document objects.
    Pinecone rejects null metadata values, so None fields are dropped.
    """
    docs = []
    for chunk in chunks:
        clean_metadata = {k: v for k, v in chunk["metadata"].items() if v is not None}
        doc = Document(
            page_content=chunk["text"],
            metadata=clean_metadata,
        )
        docs.append(doc)
    return docs


def _build_vector_ids(chunks: list[dict]) -> list[str]:
    """
    Deterministic Pinecone vector IDs based on parent_doc_id + chunk_index.
    Running the pipeline twice with the same data overwrites (upserts) instead of duplicating.
    """
    ids = []
    for chunk in chunks:
        meta = chunk["metadata"]
        parent = meta.get("parent_doc_id", "unknown")
        idx = meta.get("chunk_index", 0)
        ids.append(f"{parent}__{idx}")
    return ids


def clear_index(namespace: str = "") -> None:
    """Deletes all vectors from the Pinecone index (or a specific namespace)."""
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    index.delete(delete_all=True, namespace=namespace)
    print(f"[embedder] Cleared all vectors from index '{settings.pinecone_index_name}'.")


def embed_and_upsert(chunks: list[dict], batch_size: int = 50, dry_run: bool = False) -> None:
    """
    Embeds each chunk and upserts it into Pinecone.

    Args:
        chunks:     List of validated chunk dicts (text + metadata).
        batch_size: Number of chunks to embed and upsert per API call.
        dry_run:    If True, prints what would be upserted without calling any APIs.
    """
    if dry_run:
        print(f"[embedder] DRY RUN — would embed and upsert {len(chunks)} chunks.")
        for chunk in chunks:
            meta = chunk["metadata"]
            print(
                f"  [{meta['parent_doc_id']} chunk {meta['chunk_index']}] "
                f"{chunk['text'][:80].strip()!r}..."
            )
        return

    vector_store = _build_vector_store()
    documents = _chunks_to_documents(chunks)
    ids = _build_vector_ids(chunks)

    total = len(documents)
    upserted = 0

    for start in range(0, total, batch_size):
        batch_docs = documents[start : start + batch_size]
        batch_ids = ids[start : start + batch_size]
        vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        upserted += len(batch_docs)
        print(f"[embedder] Upserted {upserted}/{total} chunks...")

    print(f"[embedder] Done. {total} chunks upserted to Pinecone index '{settings.pinecone_index_name}'.")
