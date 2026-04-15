"""
parser.py — Text extraction from each supported file type.

Design: A single parse() dispatcher routes to a type-specific private function,
each of which wraps the appropriate langchain_community loader.  All loaders
are imported lazily (inside each function) so that a missing optional dependency
only fails when that specific parser is actually called — not at module import.

Loader choices:
  - PDF:      PyPDFLoader  — splits by page, preserving page numbers in metadata
  - DOCX:     Docx2txtLoader — straightforward, no system-level dependency
  - TXT / MD: TextLoader   — plain UTF-8 read; avoids the `unstructured` package
                              requirement that UnstructuredMarkdownLoader carries
  - CSV:      CSVLoader    — produces one Document per row formatted as
                              "column: value" lines, ideal for semantic search
  - URL:      WebBaseLoader — fetches and strips HTML via BeautifulSoup
"""

from langchain_core.documents import Document

from ingestion.loader import FileInfo


def parse(file_info: FileInfo) -> list[Document]:
    """
    Extract text from a validated source and return a list of LangChain Documents.

    Each Document carries page_content and basic source metadata from the loader.
    Chunk-level metadata (hash, chunk index, timestamp) is added later in chunker.py.

    Raises:
        ValueError:   if no parser is registered for the file type.
        ImportError:  if a required optional dependency is missing.
    """
    dispatch = {
        "pdf":  _parse_pdf,
        "docx": _parse_docx,
        "txt":  _parse_text,
        "csv":  _parse_csv,
        "md":   _parse_markdown,
        "url":  _parse_url,
    }
    fn = dispatch.get(file_info.file_type)
    if fn is None:
        raise ValueError(f"No parser registered for type: {file_info.file_type!r}")

    return fn(file_info)


# ---------------------------------------------------------------------------
# Type-specific parsers
# ---------------------------------------------------------------------------

def _parse_pdf(file_info: FileInfo) -> list[Document]:
    """
    PyPDFLoader splits by page and stores the page number in Document.metadata["page"].
    The chunker preserves this so retrieval results can cite exact page numbers.
    """
    from langchain_community.document_loaders import PyPDFLoader
    return PyPDFLoader(file_info.source).load()


def _parse_docx(file_info: FileInfo) -> list[Document]:
    from langchain_community.document_loaders import Docx2txtLoader
    return Docx2txtLoader(file_info.source).load()


def _parse_text(file_info: FileInfo) -> list[Document]:
    from langchain_community.document_loaders import TextLoader
    return TextLoader(file_info.source, encoding="utf-8").load()


def _parse_markdown(file_info: FileInfo) -> list[Document]:
    """
    TextLoader is used instead of UnstructuredMarkdownLoader to avoid the
    heavyweight `unstructured` system dependency.  For the campus markdown docs
    (tables, headings, bullet lists), plain-text extraction is sufficient — the
    chunker's markdown-aware separators handle section boundaries correctly.
    """
    from langchain_community.document_loaders import TextLoader
    return TextLoader(file_info.source, encoding="utf-8").load()


def _parse_csv(file_info: FileInfo) -> list[Document]:
    """
    CSVLoader produces one Document per row with content formatted as:
        column_name: value
        column_name: value
    This preserves row-level semantics so each row is independently retrievable.
    """
    from langchain_community.document_loaders import CSVLoader
    return CSVLoader(file_info.source).load()


def _parse_url(file_info: FileInfo) -> list[Document]:
    """
    WebBaseLoader fetches the page and strips HTML via BeautifulSoup.
    Requires: pip install beautifulsoup4 lxml
    """
    try:
        from langchain_community.document_loaders import WebBaseLoader
    except ImportError as exc:
        raise ImportError(
            "URL parsing requires beautifulsoup4: pip install beautifulsoup4 lxml"
        ) from exc

    loader = WebBaseLoader(web_paths=[file_info.source])
    return loader.load()
