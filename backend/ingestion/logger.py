"""
logger.py — Structured logging and per-file observability for the ingestion pipeline.

Design: A thin wrapper around Python's stdlib logging that also maintains a
FileIngestionRecord dataclass for machine-readable status tracking.  This lets
callers both see human-readable log lines AND programmatically inspect results
(status, chunk count, duration, error message) without parsing log strings.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Root logger configuration for the entire ingestion package.
# Uses a format that is both human-readable and easy to grep.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


@dataclass
class FileIngestionRecord:
    """
    Immutable-ish record of a single file's ingestion run.
    Populated progressively as the pipeline advances through stages.
    """

    source: str
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None
    # "pending" → "success" | "skipped" | "error"
    status: str = "pending"
    chunks_created: int = 0
    error: str | None = None
    duration_seconds: float = 0.0


class IngestionLogger:
    """
    Thin logging facade used throughout the pipeline.
    One instance is created as a module-level singleton (see bottom of file).
    """

    def __init__(self, name: str = "ingestion") -> None:
        self._log = logging.getLogger(name)
        self._start: float = 0.0

    # ------------------------------------------------------------------
    # Lifecycle helpers — each mutates and returns the record so callers
    # can do:  return logger.finish(record, chunks)
    # ------------------------------------------------------------------

    def start(self, source: str) -> FileIngestionRecord:
        record = FileIngestionRecord(source=source)
        self._start = time.perf_counter()
        self._log.info(f"[START] {source}")
        return record

    def finish(self, record: FileIngestionRecord, chunks: int) -> FileIngestionRecord:
        record.finished_at = datetime.now(timezone.utc).isoformat()
        record.chunks_created = chunks
        record.status = "success"
        record.duration_seconds = round(time.perf_counter() - self._start, 3)
        self._log.info(
            f"[DONE]  {record.source} — {chunks} chunks in {record.duration_seconds}s"
        )
        return record

    def skip(self, record: FileIngestionRecord, reason: str) -> FileIngestionRecord:
        record.finished_at = datetime.now(timezone.utc).isoformat()
        record.status = "skipped"
        record.duration_seconds = round(time.perf_counter() - self._start, 3)
        self._log.info(f"[SKIP]  {record.source} — {reason}")
        return record

    def error(self, record: FileIngestionRecord, exc: Exception) -> FileIngestionRecord:
        record.finished_at = datetime.now(timezone.utc).isoformat()
        record.status = "error"
        record.error = str(exc)
        record.duration_seconds = round(time.perf_counter() - self._start, 3)
        self._log.error(
            f"[ERROR] {record.source} — {exc}",
            exc_info=True,
        )
        return record

    def info(self, msg: str) -> None:
        self._log.info(msg)

    def warning(self, msg: str) -> None:
        self._log.warning(msg)


# Module-level singleton — all pipeline modules import this one instance.
logger = IngestionLogger()
