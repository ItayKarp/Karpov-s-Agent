"""
Chunk validator.

Every manually curated chunk must pass all checks before it can be embedded and upserted.
This is our quality gate — if a chunk fails, it surfaces as an error so the author fixes
the source document rather than silently ingesting bad data.
"""

import re

REQUIRED_METADATA_FIELDS = {
    "source",
    "page",
    "department",
    "content_type",
    "audience",
    "topic_tags",
    "academic_year",
    "semester",
    "has_deadline",
    "deadline_date",
    "urgency",
    "language",
    "chunk_index",
    "total_chunks",
    "parent_doc_id",
    "last_updated",
}

VALID_CONTENT_TYPES = {"faq", "policy", "procedure", "contact", "deadline", "form"}
VALID_AUDIENCES = {"undergraduate", "graduate", "faculty", "all"}
VALID_URGENCY = {"time_sensitive", "evergreen"}
VALID_SEMESTERS = {"fall", "spring", "summer", "all"}

# Approximate token count: 1 token ≈ 4 characters (rough OpenAI estimate)
MIN_TOKENS = 150
MAX_TOKENS = 350
CHARS_PER_TOKEN = 4


def _approx_token_count(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


class ChunkValidationError(Exception):
    pass


def validate_chunk(chunk: dict, position: str = "") -> list[str]:
    """
    Validates a single chunk dict. Returns a list of error strings.
    An empty list means the chunk is valid.
    """
    errors = []
    label = f"[{position}]" if position else ""

    text = chunk.get("text", "")
    metadata = chunk.get("metadata", {})

    # --- Text checks ---
    if not text or not text.strip():
        errors.append(f"{label} 'text' is empty.")
        return errors  # can't do further text checks

    token_count = _approx_token_count(text)
    if token_count < MIN_TOKENS:
        errors.append(
            f"{label} Text too short (~{token_count} tokens). Minimum is {MIN_TOKENS}. "
            f"Text: {text[:80]!r}..."
        )
    if token_count > MAX_TOKENS:
        errors.append(
            f"{label} Text too long (~{token_count} tokens). Maximum is {MAX_TOKENS}. "
            f"Text: {text[:80]!r}..."
        )

    # --- Metadata presence ---
    missing = REQUIRED_METADATA_FIELDS - set(metadata.keys())
    if missing:
        errors.append(f"{label} Missing metadata fields: {sorted(missing)}")

    # --- Metadata value checks ---
    content_type = metadata.get("content_type")
    if content_type not in VALID_CONTENT_TYPES:
        errors.append(
            f"{label} Invalid content_type: {content_type!r}. Must be one of {VALID_CONTENT_TYPES}."
        )

    audience = metadata.get("audience")
    if audience not in VALID_AUDIENCES:
        errors.append(
            f"{label} Invalid audience: {audience!r}. Must be one of {VALID_AUDIENCES}."
        )

    urgency = metadata.get("urgency")
    if urgency not in VALID_URGENCY:
        errors.append(
            f"{label} Invalid urgency: {urgency!r}. Must be one of {VALID_URGENCY}."
        )

    semester = metadata.get("semester")
    if semester not in VALID_SEMESTERS:
        errors.append(
            f"{label} Invalid semester: {semester!r}. Must be one of {VALID_SEMESTERS}."
        )

    topic_tags = metadata.get("topic_tags")
    if not isinstance(topic_tags, list) or len(topic_tags) == 0:
        errors.append(f"{label} 'topic_tags' must be a non-empty list.")

    has_deadline = metadata.get("has_deadline")
    deadline_date = metadata.get("deadline_date")
    if has_deadline and not deadline_date:
        errors.append(
            f"{label} has_deadline=True but deadline_date is None or missing. Provide a date string."
        )

    deadline_date = metadata.get("deadline_date")
    if deadline_date is not None:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(deadline_date)):
            errors.append(
                f"{label} deadline_date must be in YYYY-MM-DD format, got: {deadline_date!r}."
            )

    chunk_index = metadata.get("chunk_index")
    total_chunks = metadata.get("total_chunks")
    if chunk_index is not None and total_chunks is not None:
        if not isinstance(chunk_index, int) or chunk_index < 0:
            errors.append(f"{label} chunk_index must be a non-negative int.")
        if not isinstance(total_chunks, int) or total_chunks <= 0:
            errors.append(f"{label} total_chunks must be a positive int.")
        if isinstance(chunk_index, int) and isinstance(total_chunks, int):
            if chunk_index >= total_chunks:
                errors.append(
                    f"{label} chunk_index ({chunk_index}) must be less than total_chunks ({total_chunks})."
                )

    return errors


def validate_all_chunks(chunks: list[dict]) -> None:
    """
    Validates all chunks. Raises ChunkValidationError with a full report if any fail.
    Call this before embedding to catch authoring mistakes early.
    """
    all_errors = []

    for i, chunk in enumerate(chunks):
        parent_doc_id = chunk.get("metadata", {}).get("parent_doc_id", "unknown")
        chunk_index = chunk.get("metadata", {}).get("chunk_index", i)
        position = f"{parent_doc_id} chunk {chunk_index}"
        errors = validate_chunk(chunk, position=position)
        all_errors.extend(errors)

    if all_errors:
        error_report = "\n".join(f"  - {e}" for e in all_errors)
        raise ChunkValidationError(
            f"\n{len(all_errors)} validation error(s) found:\n{error_report}"
        )

    print(f"[chunker] All {len(chunks)} chunks passed validation.")
