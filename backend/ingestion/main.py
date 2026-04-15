"""
main.py — Pipeline orchestration and CLI entry point.

Stage order for every file:
  load → [idempotency check] → parse → chunk → embed → upsert → manifest write

CLI usage:
  # Ingest the bundled docs/ folder (default)
  python -m ingestion.main

  # Force re-ingest even if files are unchanged
  python -m ingestion.main --force

  # Ingest a specific file or URL
  python -m ingestion.main path/to/file.pdf
  python -m ingestion.main https://example.com/page

  # Ingest an entire directory
  python -m ingestion.main path/to/directory/

Importable API (for use from FastAPI or other code):
  from ingestion.main import ingest_file, ingest_directory, ingest_docs
"""

import json
import sys
from pathlib import Path

import ingestion.vector_store as vs
from ingestion.chunker import chunk
from ingestion.config import INGESTION_DIR, MANIFEST_PATH, SUPPORTED_EXTENSIONS
from ingestion.embedder import embed
from ingestion.loader import FileInfo, load
from ingestion.logger import FileIngestionRecord, logger
from ingestion.parser import parse


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------
# The manifest is a JSON dict:
#   { "<absolute_source_path>": { "hash": str, "chunk_count": int, "filename": str } }
#
# It is written atomically via a temp-then-rename pattern so a crash mid-write
# never leaves a half-written file that breaks the next run.


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except json.JSONDecodeError:
            logger.warning("Manifest file is corrupt — starting fresh")
    return {}


def _save_manifest(manifest: dict) -> None:
    tmp = MANIFEST_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2))
    tmp.replace(MANIFEST_PATH)  # atomic on POSIX; best-effort on Windows


# ---------------------------------------------------------------------------
# Single-file ingestion
# ---------------------------------------------------------------------------


def ingest_file(source: str, force: bool = False) -> FileIngestionRecord:
    """
    Run the full ingestion pipeline for a single file or URL.

    Args:
        source: Absolute or relative file path, or an http(s) URL.
        force:  Skip the manifest check and re-ingest even if content is unchanged.
                Use this after editing a file to guarantee fresh vectors.

    Returns:
        FileIngestionRecord with status, chunk count, duration, and any error.
    """
    record = logger.start(source)
    manifest = _load_manifest()

    try:
        # ── Stage 1: Load & validate ─────────────────────────────────────────
        file_info: FileInfo = load(source)

        # ── Stage 2: Idempotency check ───────────────────────────────────────
        cached = manifest.get(file_info.source, {})
        if not force and cached.get("hash") == file_info.file_hash:
            return logger.skip(record, "content unchanged (hash match in manifest)")

        # If the file was updated (hash changed), purge stale Qdrant vectors
        # so the old content doesn't pollute retrieval results.
        old_hash = cached.get("hash")
        if old_hash and old_hash != file_info.file_hash:
            vs.delete_by_hash(old_hash)

        # ── Stage 3: Parse ───────────────────────────────────────────────────
        documents = parse(file_info)
        if not documents:
            return logger.skip(record, "parser returned no content")

        # ── Stage 4: Chunk ───────────────────────────────────────────────────
        chunks = chunk(documents, file_info)
        logger.info(
            f"{file_info.filename}: {len(documents)} doc(s) → {len(chunks)} chunk(s)"
        )

        # ── Stage 5: Embed ───────────────────────────────────────────────────
        vectors = embed(chunks)

        # ── Stage 6: Upsert ──────────────────────────────────────────────────
        n_written = vs.upsert(chunks, vectors)

        # ── Stage 7: Update manifest ─────────────────────────────────────────
        manifest[file_info.source] = {
            "hash":        file_info.file_hash,
            "chunk_count": n_written,
            "filename":    file_info.filename,
        }
        _save_manifest(manifest)

        return logger.finish(record, n_written)

    except Exception as exc:
        return logger.error(record, exc)


# ---------------------------------------------------------------------------
# Batch ingestion helpers
# ---------------------------------------------------------------------------


def ingest_directory(
    directory: str | Path, force: bool = False
) -> list[FileIngestionRecord]:
    """
    Ingest all supported files found directly inside a directory (non-recursive).
    Files are processed in alphabetical order for deterministic output.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {directory!r}")

    files = sorted(
        f for f in dir_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    logger.info(f"Found {len(files)} supported file(s) in {dir_path}")
    return [ingest_file(str(f), force=force) for f in files]


def ingest_docs(force: bool = False) -> list[FileIngestionRecord]:
    """
    Convenience function: ingest the bundled docs/ folder that ships with
    this package.  This is the default action when main.py is run with no args.
    """
    return ingest_directory(INGESTION_DIR / "docs", force=force)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _print_summary(records: list[FileIngestionRecord]) -> None:
    icons = {"success": "✓", "skipped": "–", "error": "✗"}
    print("\n── Ingestion Summary " + "─" * 47)
    for r in records:
        icon = icons.get(r.status, "?")
        name = r.source.split("/")[-1]
        if r.status == "success":
            detail = f"{r.chunks_created} chunks  ({r.duration_seconds}s)"
        elif r.status == "error":
            detail = f"ERROR: {r.error}"
        else:
            detail = f"skipped  ({r.duration_seconds}s)"
        print(f"  {icon}  {name:<42} {detail}")

    success = sum(1 for r in records if r.status == "success")
    skipped = sum(1 for r in records if r.status == "skipped")
    errors  = sum(1 for r in records if r.status == "error")
    total   = sum(r.chunks_created for r in records)
    print("─" * 67)
    print(
        f"  {success} ingested  |  {skipped} skipped  |  {errors} error(s)"
        f"  |  {total} total chunks written\n"
    )


if __name__ == "__main__":
    # Ensure the Qdrant collection exists before any writes.
    vs.ensure_collection()

    args = sys.argv[1:]
    force = "--force" in args
    sources = [a for a in args if not a.startswith("--")]

    if not sources:
        # Default: ingest the bundled docs/ directory.
        records = ingest_docs(force=force)
    else:
        records = []
        for src in sources:
            p = Path(src)
            if p.is_dir():
                records.extend(ingest_directory(p, force=force))
            else:
                records.append(ingest_file(src, force=force))

    _print_summary(records)
    # Non-zero exit code if any file errored — useful for CI pipelines.
    sys.exit(1 if any(r.status == "error" for r in records) else 0)
