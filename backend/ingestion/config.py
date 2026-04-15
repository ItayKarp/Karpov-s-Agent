"""
config.py — All configuration, constants, and environment settings for the ingestion pipeline.

Design: Mirrors the pydantic-settings pattern used in app/core/config.py so that
this pipeline shares the same .env file from the project root without duplicating values.
A separate IngestionSettings class keeps concerns isolated — adding new app-level env
vars never breaks this module (extra="ignore").
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path to the ingestion package directory.
# All other paths are derived from this so the pipeline works regardless of CWD.
INGESTION_DIR: Path = Path(__file__).parent

# Shared .env in the backend root — same file used by the main FastAPI app.
ENV_FILE: Path = INGESTION_DIR.parent / ".env"

# ---------------------------------------------------------------------------
# Chunking strategy
# ---------------------------------------------------------------------------
# 800 characters (~200 tokens for English prose) keeps each chunk semantically
# coherent for a campus FAQ / policy document domain.  Shorter chunks improve
# retrieval precision; larger chunks improve context richness.
CHUNK_SIZE: int = 800

# 100-character overlap (~25 tokens) prevents sentences from being split across
# chunk boundaries — especially important for headings followed by body text.
CHUNK_OVERLAP: int = 100

# ---------------------------------------------------------------------------
# Supported input types
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".pdf", ".docx", ".txt", ".csv", ".md", ".markdown"}
)

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------
# text-embedding-3-small: 1536 dimensions, very cost-effective, strong
# retrieval quality for English-language campus documents.
# Upgrade to text-embedding-3-large (3072 dims) if quality needs improvement.
EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBEDDING_DIMENSIONS: int = 1536

# Max texts per OpenAI API call.  OpenAI's hard limit is 2048; 100 is
# conservative to stay within rate-limit quotas while maximising throughput.
EMBEDDING_BATCH_SIZE: int = 100

# ---------------------------------------------------------------------------
# Qdrant
# ---------------------------------------------------------------------------
QDRANT_COLLECTION_NAME: str = "ai-dual-agent"

# ---------------------------------------------------------------------------
# Manifest (idempotency store)
# ---------------------------------------------------------------------------
# A lightweight JSON file mapping each source path → {hash, chunk_count}.
# Used to skip unchanged files and to identify stale Qdrant points when a
# file is updated between pipeline runs.
MANIFEST_PATH: Path = INGESTION_DIR / ".ingestion_manifest.json"


class IngestionSettings(BaseSettings):
    """Loads credentials from the shared .env file."""

    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",  # silently ignore unrelated keys from the shared .env
    )


# Module-level singleton — import `settings` everywhere; never re-instantiate.
settings = IngestionSettings()
