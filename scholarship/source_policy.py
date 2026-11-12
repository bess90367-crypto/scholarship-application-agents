"""Deterministic routing helpers for source coverage.

Private URLs and applicant data do not belong in this module.
"""

RAW_DOWNLOAD_LIMIT_BYTES = 256 * 1024 * 1024
RECOMMENDED_SPLIT_BYTES = 200 * 1024 * 1024


def large_file_route(
    size_bytes,
    indexed_text_complete=False,
    verified_split_copy=False,
    direct_stream_available=False,
    browser_available=True,
):
    """Return the next required handling route for a Drive PDF."""
    if not isinstance(size_bytes, int) or size_bytes < 0:
        raise ValueError("size_bytes must be a non-negative integer")
    if indexed_text_complete:
        return "indexed_text"
    if size_bytes <= RAW_DOWNLOAD_LIMIT_BYTES:
        return "raw_download"
    if direct_stream_available:
        return "direct_stream_download_and_split"
    if verified_split_copy:
        return "verified_split_copy"
    if browser_available:
        return "work_browser_download_and_split"
    return "user_split_required"


def batch_is_complete(source_statuses):
    """Only fully read or explicitly excluded/duplicate sources can close a batch."""
    allowed = {"fully_read", "verified_duplicate", "explicitly_out_of_scope"}
    statuses = list(source_statuses)
    return bool(statuses) and all(status in allowed for status in statuses)
