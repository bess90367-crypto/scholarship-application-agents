import argparse
import json
from pathlib import Path
from .core import score, validate_rank, discrepancies


def pdf_text(source, destination):
    from pypdf import PdfReader
    reader = PdfReader(source)
    pages = []
    manifest = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        # A heuristic only: text may be corrupt or unrelated to the visible page.
        needs_review = len(''.join(text.split())) < 30
        pages.append(f'=== PAGE {index} ===\n{text}\n')
        manifest.append({'page': index, 'characters': len(text),
                         'ocr_candidate': needs_review, 'visual_verification_required': True})
    Path(destination).write_text('\n'.join(pages), encoding='utf-8')
    Path(str(destination) + '.pages.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'pages': len(pages), 'ocr_candidates': [p['page'] for p in manifest if p['ocr_candidate']],
            'notice': 'Text-layer extraction only. OCR candidates require image rendering and OCR/transcription before downstream filling.'}


def template(source):
    from openpyxl import load_workbook
    workbook = load_workbook(source, data_only=False)
    sheets = []
    for sheet in workbook:
        sheets.append({'name': sheet.title, 'dimensions': sheet.calculate_dimension(),
                       'state': sheet.sheet_state,
                       'merged_ranges': [str(r) for r in sheet.merged_cells.ranges],
                       'hidden_rows': [i for i, d in sheet.row_dimensions.items() if d.hidden],
                       'hidden_columns': [i for i, d in sheet.column_dimensions.items() if d.hidden],
                       'row_heights': {str(i): d.height for i, d in sheet.row_dimensions.items() if d.height is not None},
                       'column_widths': {i: d.width for i, d in sheet.column_dimensions.items() if d.width is not None},
                       'validations': [{'type': v.type, 'range': str(v.sqref), 'formula1': v.formula1} for v in sheet.data_validations.dataValidation],
                       'cells': [{'coordinate': c.coordinate, 'value': cell_value(c.value),
                                  'type': c.data_type, 'number_format': c.number_format, 'style_id': c.style_id}
                                 for row in sheet for c in row if c.value is not None or c.has_style]})
    return {'sheets': sheets, 'defined_names': {k: v.attr_text for k, v in workbook.defined_names.items()},
            'notice': 'Inspection does not calculate formula caches; review fills/formatting visually before delivery.'}


def cell_value(value):
    """Keep numbers typed and array formula definitions inspectable."""
    if hasattr(value, 'text') and hasattr(value, 'ref'):
        return {'formula': value.text, 'ref': value.ref}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def main():
    parser = argparse.ArgumentParser(description='Private scholarship document helpers')
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('score', 'verify', 'inspect-template'):
        commands.add_parser(command).add_argument('input')
    pdf = commands.add_parser('prepare-pdf')
    pdf.add_argument('input')
    pdf.add_argument('output')
    args = parser.parse_args()
    try:
        if args.command == 'prepare-pdf':
            result = pdf_text(args.input, args.output)
        elif args.command == 'inspect-template':
            result = template(args.input)
        else:
            document = json.loads(Path(args.input).read_text(encoding='utf-8-sig'))
            result = score(document)
            if args.command == 'verify':
                result = {'score': result, 'ranks': [validate_rank(r) for r in document.get('ranks', [])],
                          'discrepancies': discrepancies(document)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, ImportError) as exc:
        parser.exit(2, f'Blocked: {exc}\n')


if __name__ == '__main__':
    main()
