"""Compare original OOXML worksheet structure while permitting value replacement.

Use private sheet-part mappings, not applicant names in public fixtures. This is
a structural regression guard, not a renderer or proof of data correctness.
"""
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re

MAIN = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def _tree(element):
    return (element.tag, tuple(sorted(element.attrib.items())),
            (element.text or '').strip(), tuple(_tree(child) for child in element))


def normalize_self_references(formula, own_sheet):
    """Normalize exact own-sheet tokens, excluding strings and external refs."""
    if not own_sheet:
        return formula
    quoted = "'" + own_sheet.replace("'", "''") + "'"
    pattern = re.compile(r"(?<![\w.\]':])" + '(?:' + re.escape(quoted) + '|' +
                         re.escape(own_sheet) + r')!')
    # Double-quoted Excel literals may contain sheet-looking text or escaped quotes.
    pieces = re.split(r'("(?:[^"]|"")*")', formula)
    for index in range(0, len(pieces), 2):
        pieces[index] = pattern.sub('__SELF__!', pieces[index])
    return ''.join(pieces)


def worksheet_signature(xml, own_sheet=None):
    """Ignore cell values/types; retain formulas and every format-bearing node."""
    root = ET.fromstring(xml)
    for cell in root.iter(MAIN + 'c'):
        cell.attrib.pop('t', None)
        for child in list(cell):
            if child.tag in (MAIN + 'v', MAIN + 'is'):
                cell.remove(child)
            elif child.tag == MAIN + 'f' and child.text:
                child.text = normalize_self_references(child.text, own_sheet)
    return _tree(root)


def format_differences(template_path, output_path, sheet_pairs, sheet_names=None):
    """Return differences for explicit (template_part, output_part) pairs.

    Callers must cover every output worksheet. Cell positions must already exist
    in the copied template; inserting even an unstyled cell is a difference.
    Non-input values, workbook names and external resources need separate checks.
    Optional sheet_names maps output part to (original own-name, new own-name),
    permitting only exact self-reference renaming while keeping all other logic.
    """
    pairs = list(sheet_pairs)
    if not pairs:
        raise ValueError('at least one explicit worksheet pair is required')
    differences = []
    with ZipFile(template_path) as template, ZipFile(output_path) as output:
        output_parts = {name for name in output.namelist()
                        if name.startswith('xl/worksheets/') and name.endswith('.xml')
                        and '/_rels/' not in name}
        targets = [target for _, target in pairs]
        if len(targets) != len(set(targets)) or set(targets) != output_parts:
            raise ValueError('worksheet mapping must cover every output worksheet exactly once')
        for source, target in pairs:
            names = (sheet_names or {}).get(target, (None, None))
            if worksheet_signature(template.read(source), names[0]) != worksheet_signature(output.read(target), names[1]):
                differences.append('worksheet structure: ' + target)
        style_parts = {name for archive in (template, output) for name in archive.namelist()
                       if name == 'xl/styles.xml' or name.startswith('xl/theme/')}
        for name in sorted(style_parts):
            if name not in template.namelist() or name not in output.namelist():
                differences.append('missing style/theme part: ' + name)
            elif _tree(ET.fromstring(template.read(name))) != _tree(ET.fromstring(output.read(name))):
                differences.append('style/theme content: ' + name)
    return differences
