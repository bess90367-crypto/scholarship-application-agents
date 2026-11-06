"""Check private batch coverage without publishing source identifiers."""


def batch_coverage(files):
    """A page is reviewed when its relevant content or attachment summary is saved.

    This checks bookkeeping only, not transcription accuracy or eligibility.
    Stable file IDs are caller-owned private identifiers, never filename guesses.
    """
    if not files:
        raise ValueError('source inventory is required')
    seen, missing = set(), {}
    for item in files:
        key, count = item.get('source_id'), item.get('page_count')
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError('unique source identifier required')
        seen.add(key)
        if type(count) is not int or count < 1:
            raise ValueError('verified positive page count required')
        pages = item.get('reviewed_pages', [])
        if any(type(p) is not int or p < 1 or p > count for p in pages):
            raise ValueError('reviewed page outside source bounds')
        gaps = sorted(set(range(1, count + 1)) - set(pages))
        if gaps:
            missing[key] = gaps
    return {'complete': not missing, 'source_count': len(seen), 'missing_pages': missing}
