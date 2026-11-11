"""Private workbook naming and explicit ROC-semester selection helpers."""
import hashlib
import re
from .core import identifier


def semester(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]{0,2}-[12]', value):
        raise ValueError('explicit ROC semester required, for example 115-1')
    return value


def semester_from_request(text):
    """Extract exactly one ROC semester from a natural-language request."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('request text required')
    matches = sorted(set(re.findall(r'(?<![0-9])([1-9][0-9]{0,2}-[12])(?![0-9])', text)))
    if len(matches) != 1:
        raise ValueError('request must contain exactly one ROC semester')
    return semester(matches[0])


def _semester_folder_component_matches(component, requested):
    """Match canonical semester folder names without accepting copies."""
    return component == requested or component == requested + '獎學金申請資料'


def semester_matches(folder_or_path, requested):
    """Match a canonical semester folder path component; never infer from transcripts."""
    requested = semester(requested)
    if not isinstance(folder_or_path, str):
        raise ValueError('folder/path must be text')
    return any(
        _semester_folder_component_matches(component, requested)
        for component in folder_or_path.replace('\\', '/').split('/')
    )


def select_semester_folder(folder_paths, requested):
    """Return the single folder path matching the requested ROC semester."""
    if not isinstance(folder_paths, (list, tuple)):
        raise ValueError('folder paths must be a list or tuple')
    matches = [path for path in folder_paths if semester_matches(path, requested)]
    if len(matches) != 1:
        raise ValueError('expected exactly one matching semester folder')
    return matches[0]


def _base_name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('confirmed applicant name required')
    value = re.sub(r'[\\/*?:\[\]\x00-\x1f]', '_', value.strip()).strip("'")
    if not value:
        raise ValueError('applicant name has no usable characters')
    return value[:31].rstrip("'")


def applicant_sheets(applicants, reserved=('計算模板', '(勿動!!!!!!!)參數清單表', 'History')):
    """Return student-id -> sheet-name; stable regardless of input order.

    Real IDs and names belong only in private inputs/outputs. A digest suffix is
    a naming disambiguator, not anonymization and not a public identifier.
    """
    rows = []
    identities = set()
    used = {name.casefold() for name in reserved} | {'history'}
    for item in applicants:
        student_id = identifier(item.get('student_id'))
        if student_id in identities:
            raise ValueError('duplicate student identity; merge evidence before naming')
        identities.add(student_id)
        rows.append((student_id, _base_name(item.get('name'))))
    counts = {}
    for _, name in rows:
        counts[name.casefold()] = counts.get(name.casefold(), 0) + 1
    result = {}
    for key, name in sorted(rows):
        if counts[name.casefold()] == 1 and name.casefold() not in used:
            result[key] = name
            used.add(name.casefold())
    for key, base in sorted(rows):
        if key in result:
            continue
        digest = hashlib.sha256(key.encode('utf-8')).hexdigest()[:10]
        count = 0
        while True:
            suffix = '-' + digest + (f'-{count}' if count else '')
            candidate = base[:31-len(suffix)] + suffix
            if candidate.casefold() not in used:
                break
            count += 1
        result[key] = candidate
        used.add(candidate.casefold())
    return result
