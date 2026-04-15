"""
vector_store.py — Qdrant collection management, upsert, existence check, and deletion.

Design: Uses the raw qdrant_client (not a LangChain wrapper) so we have full
control over point IDs, payload filters, and collection bootstrapping — all
required for correct idempotency behaviour.

Idempotency strategy (two-layer):
  1. Deterministic point IDs — UUID5(namespace, "{file_hash}_{chunk_index}").
     Upserting the same chunk always produces the same ID, so identical content
     is a pure overwrite with no duplication at Qdrant's storage layer.

  2. Hash-based deletion — when a file is *updated* (its hash changes), the
     pipeline calls delete_by_hash(old_hash) to remove every stale point before
     upserting the new ones.  The local manifest (main.py) provides the old hash.

Collection bootstrap:
  ensure_collection() is called once at pipeline startup.  It creates the
  collection and a keyword index on the file_hash payload field if they do not
  exist.  The keyword index makes filter-based scroll and delete O(log n) rather
  than a full scan.
"""

import uuid
from typing import Any

from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from ingestion.config import (
    EMBEDDING_DIMENSIONS,
    QDRANT_COLLECTION_NAME,
    settings,
)
from ingestion.logger import logger


# ---------------------------------------------------------------------------
# Stable UUID namespace for deterministic point ID generation.
# Any fixed UUID works — this one is arbitrary and project-specific.
# ---------------------------------------------------------------------------
_ID_NAMESPACE = uuid.UUID("c0ffee00-dead-beef-cafe-000000000001")

COLLECTION = QDRANT_COLLECTION_NAME


def _point_id(file_hash: str, chunk_index: int) -> str:
    """Return a deterministic UUID5 string for a given (hash, chunk) pair."""
    return str(uuid.uuid5(_ID_NAMESPACE, f"{file_hash}_{chunk_index}"))


# ---------------------------------------------------------------------------
# Singleton client — one TCP connection pool for the entire pipeline run.
# ---------------------------------------------------------------------------
_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key or None,
    timeout=30,
)


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------

def ensure_collection() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    Safe to call multiple times — checks before creating (idempotent).

    Also creates a keyword payload index on 'file_hash' so that
    filter-based scroll() and delete() are efficient at scale.
    """
    existing = {c.name for c in _client.get_collections().collections}

    if COLLECTION not in existing:
        _client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE,  # standard for OpenAI embeddings
            ),
        )
        # Index file_hash for O(log n) filter performance.
        _client.create_payload_index(
            collection_name=COLLECTION,
            field_name="file_hash",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        logger.info(f"Created Qdrant collection '{COLLECTION}' with file_hash index")
    else:
        logger.info(f"Qdrant collection '{COLLECTION}' already exists")


# ---------------------------------------------------------------------------
# Idempotency helpers
# ---------------------------------------------------------------------------

def exists(file_hash: str) -> bool:
    """
    Return True if at least one point with this file_hash is already stored.
    Used by main.py to skip re-embedding unchanged files (force=False).
    """
    points, _ = _client.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
        ),
        limit=1,
        with_payload=False,
        with_vectors=False,
    )
    return len(points) > 0


def delete_by_hash(file_hash: str) -> None:
    """
    Delete every point associated with a given file hash.
    Called before re-ingesting an updated file to purge stale vectors.
    """
    _client.delete(
        collection_name=COLLECTION,
        points_selector=FilterSelector(
            filter=Filter(
                must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
            )
        ),
    )
    logger.info(f"Deleted stale points for hash {file_hash[:12]}…")


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert(chunks: list[Document], vectors: list[list[float]]) -> int:
    """
    Write chunk vectors and their payloads into Qdrant.

    Point IDs are deterministic (see _point_id) so re-ingesting the same
    content simply overwrites the existing points without creating duplicates.

    Args:
        chunks:  List of Documents with metadata populated by chunker.py.
        vectors: Parallel list of embedding vectors from embedder.py.

    Returns:
        Number of points written.
    """
    if len(chunks) != len(vectors):
        raise ValueError(
            f"Chunks/vectors length mismatch: {len(chunks)} vs {len(vectors)}"
        )

    points: list[PointStruct] = [
        PointStruct(
            id=_point_id(chunk.metadata["file_hash"], chunk.metadata["chunk_index"]),
            vector=vector,
            payload=_build_payload(chunk),
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    # Send in batches of 100 to keep individual gRPC payloads manageable.
    BATCH = 100
    for i in range(0, len(points), BATCH):
        _client.upsert(
            collection_name=COLLECTION,
            points=points[i : i + BATCH],
        )

    logger.info(f"Upserted {len(points)} point(s) into '{COLLECTION}'")
    return len(points)


def _build_payload(chunk: Document) -> dict[str, Any]:
    """
    Flatten chunk metadata and text into the Qdrant point payload.
    'text' is stored alongside the vector so retrieval can return raw passages
    to the LLM without a second database lookup.
    """
    return {
        "text":        chunk.page_content,
        "source":      chunk.metadata["source"],
        "filename":    chunk.metadata["filename"],
        "file_type":   chunk.metadata["file_type"],
        "file_hash":   chunk.metadata["file_hash"],
        "page":        chunk.metadata["page"],
        "chunk_index": chunk.metadata["chunk_index"],
        "ingested_at": chunk.metadata["ingested_at"],
    }
