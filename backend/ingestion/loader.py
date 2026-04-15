from ingestion.documents import (
    academic_calendar,
    financial_aid_faq,
    registration_faq,
    student_handbook,
    campus_map_and_locations,
    clubs_and_organizations,
    course_catalog,
    dining_and_housing,
    it_services,
    library_services,
)

ALL_DOCUMENT_MODULES = [
    academic_calendar,
    financial_aid_faq,
    registration_faq,
    student_handbook,
    campus_map_and_locations,
    clubs_and_organizations,
    course_catalog,
    dining_and_housing,
    it_services,
    library_services,
]


def load_all_chunks() -> list[dict]:
    """
    Aggregates all manually curated chunks from every document module.
    Returns a flat list of chunk dicts, each with 'text' and 'metadata' keys.
    """
    all_chunks = []
    for module in ALL_DOCUMENT_MODULES:
        all_chunks.extend(module.CHUNKS)
    return all_chunks
