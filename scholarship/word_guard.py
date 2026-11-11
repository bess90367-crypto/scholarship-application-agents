"""Exact structural guards for explicitly selected DOCX regions.

Selectors are reviewed, zero-based top-level body block indices. This helper
does not infer semantic boundaries or prove applicant data/layout correctness.
"""
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def _blocks(package):
    root = ET.fromstring(package.read('word/document.xml'))
    body = root.find(W + 'body')
    if body is None:
        raise ValueError('DOCX document has no body')
    return list(body)


def _canonical(element):
    return ET.canonicalize(ET.tostring(element, encoding='unicode'))


def verify_preserved_regions(template, output, regions, immutable_parts=()):
    """Return mismatches; reject missing/ambiguous selector specifications.

    regions maps a nonempty label to (source_indices, output_indices).
    Explicit output indices allow approved applicant-row insertions before
    a protected section without requiring the section's original position.
    immutable_parts names package members whose bytes must remain identical.
    """
    if not regions:
        raise ValueError('At least one reviewed protected region is required')
    mismatches = []
    with ZipFile(template) as original, ZipFile(output) as result:
        source_blocks, output_blocks = _blocks(original), _blocks(result)
        for label, selectors in regions.items():
            if not isinstance(label, str) or not label.strip() or len(selectors) != 2:
                raise ValueError('Invalid protected region specification')
            selected = []
            for indices, blocks in zip(selectors, (source_blocks, output_blocks)):
                indices = list(indices)
                if (not indices or any(type(i) is not int or i < 0 or i >= len(blocks)
                                       for i in indices)
                        or indices != sorted(set(indices))):
                    raise ValueError('Protected indices must be nonempty, unique, ordered, in range')
                selected.append([_canonical(blocks[i]) for i in indices])
            if selected[0] != selected[1]:
                mismatches.append({'region': label, 'reason': 'protected XML changed'})
        for name in immutable_parts:
            if name not in original.namelist() or name not in result.namelist():
                mismatches.append({'part': name, 'reason': 'required package part missing'})
            elif original.read(name) != result.read(name):
                mismatches.append({'part': name, 'reason': 'package part changed'})
    return {'passed': not mismatches, 'regions_checked': len(regions), 'mismatches': mismatches}
