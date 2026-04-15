"""
embedder.py — Embedding generation via OpenAI text-embedding-3-small.

Design: A thin wrapper around langchain_openai.OpenAIEmbeddings that adds:
  1. Explicit batching — we control batch boundaries and log progress so large
     files don't silently stall without feedback.
  2. Single retry per batch — handles transient network blips without
     complicating the caller with retry logic.

The embedder is a module-level singleton so the underlying HTTP client
(and its connection pool) is reused across all files in a pipeline run.
"""

import time
from typing import Iterator

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from ingestion.config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, settings
from ingestion.logger import logger


# One client for the entire pipeline run.
_embedder = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    openai_api_key=settings.openai_api_key,
)


def _batched(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed(chunks: list[Document]) -> list[list[float]]:
    """
    Generate an embedding vector for every chunk, in order.

    Batches are sent sequentially (not concurrently) to stay within OpenAI's
    rate limits.  For large corpora, consider adding asyncio + semaphore here.

    Args:
        chunks: List of Document objects with page_content to embed.

    Returns:
        List of float vectors, one per chunk, same order as input.

    Raises:
        RuntimeError: if a batch fails after 2 attempts.
    """
    texts = [c.page_content for c in chunks]
    vectors: list[list[float]] = []

    total_batches = (len(texts) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE

    for batch_num, batch in enumerate(_batched(texts, EMBEDDING_BATCH_SIZE), start=1):
        logger.info(
            f"Embedding batch {batch_num}/{total_batches} ({len(batch)} texts)"
        )
        for attempt in (1, 2):
            try:
                batch_vectors = _embedder.embed_documents(batch)
                vectors.extend(batch_vectors)
                break
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(
                        f"Embedding failed after 2 attempts on batch {batch_num}: {exc}"
                    ) from exc
                logger.warning(
                    f"Batch {batch_num} attempt {attempt} failed ({exc}), retrying in 3s…"
                )
                time.sleep(3)

    return vectors
