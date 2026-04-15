"""
chunker.py — Splitting parsed documents into semantically meaningful chunks.

Design: RecursiveCharacterTextSplitter with a markdown-aware separator list.
The splitter tries each separator in order, falling back to the next only when
a chunk still exceeds CHUNK_SIZE.  Markdown headings and horizontal rules are
tried first so chunk boundaries naturally align with document sections.

Metadata attached to every chunk (all fields are Qdrant-filterable):
  - source:       absolute file path or URL
  - filename:     basename of the file (used in citation)
  - file_type:    pdf | docx | txt | csv | md | url
  - file_hash:    SHA-256 of the source — primary idempotency key
  - page:         page number from the original document (PDFs only, else 0)
  - chunk_index:  0-based position within this file's chunk sequence
  - ingested_at:  ISO-8601 UTC timestamp of this pipeline run
"""

from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingestion.config import CHUNK_SIZE, CHUNK_OVERLAP
from ingestion.loader import FileInfo


# Ordered from coarsest to finest structural boundary.
# "keep_separator=True" preserves the heading marker in the chunk text so
# the LLM can still see which section a chunk belongs to.
_SEPARATORS: list[str] = [
    "\n## ",    # H2 heading
    "\n### ",   # H3 heading
    "\n#### ",  # H4 heading
    "\n---",    # markdown horizontal rule
    "\n\n",     # paragraph break
    "\n",       # line break
    " ",        # word boundary
    "",         # character-level last resort
]

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=_SEPARATORS,
    keep_separator=True,
)


def chunk(documents: list[Document], file_info: FileInfo) -> list[Document]:
    """
    Split a list of parsed Documents into overlapping chunks and attach
    full provenance metadata to every resulting chunk.

    Args:
        documents:  Output from parser.parse() — one Document per page/row/file.
        file_info:  FileInfo from loader.load() — supplies hash and type info.

    Returns:
        List of Documents ready for embedding.  Each has a populated metadata
        dict and page_content containing the raw chunk text.
    """
    raw_chunks: list[Document] = _splitter.split_documents(documents)

    ingested_at = datetime.now(timezone.utc).isoformat()
    enriched: list[Document] = []

    for idx, doc in enumerate(raw_chunks):
        # Carry forward the page number when the loader set it (PyPDFLoader).
        # For all other loaders this defaults to 0 (single logical "page").
        page = doc.metadata.get("page", 0)

        doc.metadata = {
            "source":      file_info.source,
            "filename":    file_info.filename,
            "file_type":   file_info.file_type,
            "file_hash":   file_info.file_hash,
            "page":        page,
            "chunk_index": idx,
            "ingested_at": ingested_at,
        }
        enriched.append(doc)

    return enriched
