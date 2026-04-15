"""
Ingestion pipeline entry point.

Usage (from the backend/ directory):
    uv run python -m ingestion.pipeline              # embed and upsert all chunks
    uv run python -m ingestion.pipeline --dry-run    # validate and preview without calling APIs
    uv run python -m ingestion.pipeline --clear      # delete all vectors, then re-ingest
    uv run python -m ingestion.pipeline --clear --dry-run  # show what would be cleared/ingested
"""

import argparse
import sys

from ingestion.loader import load_all_chunks
from ingestion.chunker import validate_all_chunks, ChunkValidationError
from ingestion.embedder import embed_and_upsert, clear_index


def run(dry_run: bool = False, clear: bool = False) -> None:
    print("[pipeline] Loading chunks...")
    chunks = load_all_chunks()
    print(f"[pipeline] Loaded {len(chunks)} chunks from {_count_documents(chunks)} documents.")

    print("[pipeline] Validating chunks...")
    try:
        validate_all_chunks(chunks)
    except ChunkValidationError as e:
        print(f"[pipeline] VALIDATION FAILED:{e}", file=sys.stderr)
        sys.exit(1)

    if clear:
        if dry_run:
            print("[pipeline] DRY RUN — would clear the Pinecone index before upserting.")
        else:
            print("[pipeline] Clearing Pinecone index...")
            clear_index()

    print("[pipeline] Embedding and upserting...")
    embed_and_upsert(chunks, dry_run=dry_run)

    print("[pipeline] Complete.")


def _count_documents(chunks: list[dict]) -> int:
    return len({c["metadata"].get("parent_doc_id") for c in chunks})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the campus RAG ingestion pipeline.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate chunks and preview output without calling any external APIs.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all existing vectors from the Pinecone index before upserting.",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run, clear=args.clear)
