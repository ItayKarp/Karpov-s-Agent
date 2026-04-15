"""
loader.py — File loading, validation, and SHA-256 hashing.

Design: The loader's sole responsibility is to validate that a source is
readable and supported, then describe it via a FileInfo dataclass.  It does
NOT read content — that is the parser's job.  This separation means the
idempotency check (hash comparison) can happen before any expensive parsing
or embedding calls.

Supported inputs:
  - Local files: .pdf, .docx, .txt, .csv, .md, .markdown
  - HTTP/HTTPS URLs (content fetched lazily by the parser)
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ingestion.config import SUPPORTED_EXTENSIONS


@dataclass(frozen=True)
class FileInfo:
    """Describes a validated source before any content is read."""

    source: str       # Resolved absolute file path or original URL string
    file_type: str    # One of: pdf | docx | txt | csv | md | url
    file_hash: str    # SHA-256 hex digest (content hash for files, URL hash for URLs)
    filename: str     # Human-readable name used in chunk metadata and logs
    is_url: bool = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"}


def _extension_to_type(ext: str) -> str:
    mapping = {
        ".md":       "md",
        ".markdown": "md",
        ".pdf":      "pdf",
        ".docx":     "docx",
        ".txt":      "txt",
        ".csv":      "csv",
    }
    return mapping[ext]


def _hash_file(path: Path) -> str:
    """Stream the file through SHA-256 in 64 KB blocks to handle large files."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65_536), b""):
            h.update(block)
    return h.hexdigest()


def _hash_string(value: str) -> str:
    """Stable hash for URL strings (no content fetch at load time)."""
    return hashlib.sha256(value.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load(source: str) -> FileInfo:
    """
    Validate a source path or URL and return a FileInfo describing it.

    Raises:
        FileNotFoundError: if the path does not exist on disk.
        ValueError:        if the extension is not in SUPPORTED_EXTENSIONS,
                           or if the path points to a directory.
    """
    if _is_url(source):
        parsed = urlparse(source)
        # Build a readable filename from the URL so chunk metadata is meaningful.
        filename = (parsed.netloc + parsed.path).replace("/", "_").strip("_") or "url"
        return FileInfo(
            source=source,
            file_type="url",
            # Hash the URL string itself — content is fetched by the parser.
            # The manifest will therefore re-fetch if the URL changes, but not
            # if only the content at a stable URL changes.  For mutable URLs,
            # pass --force to bypass the manifest check.
            file_hash=_hash_string(source),
            filename=filename,
            is_url=True,
        )

    path = Path(source)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {source!r}")
    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {source!r}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension {ext!r}. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    return FileInfo(
        source=str(path.resolve()),
        file_type=_extension_to_type(ext),
        file_hash=_hash_file(path),
        filename=path.name,
    )
