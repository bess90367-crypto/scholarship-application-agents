from io import BytesIO
from zipfile import ZipFile
import unittest
from scholarship.format_guard import worksheet_signature, format_differences, normalize_self_references


SHEET = '''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="1" width="18"/></cols>
<sheetData><row r="1" ht="24"><c r="A1" s="1" t="inlineStr"><is><t>Example</t></is></c>
<c r="B1" s="2"><f>SUM(A2:A3)</f><v>12</v></c></row></sheetData>
<mergeCells count="1"><mergeCell ref="A2:B2"/></mergeCells>
<pageSetup orientation="landscape"/></worksheet>'''


def archive(sheet=SHEET, style='<styleSheet/>'):
    result = BytesIO()
    with ZipFile(result, 'w') as zipped:
        zipped.writestr('xl/worksheets/sheet1.xml', sheet)
        zipped.writestr('xl/styles.xml', style)
        zipped.writestr('xl/theme/theme1.xml', '<theme/>')
    return result


class StrictFormatTests(unittest.TestCase):
    def test_only_exact_self_reference_rename_is_allowed(self):
        source = SHEET.replace('SUM(A2:A3)', "SUM(Template!E2,'Template'!F2)")
        output = SHEET.replace('SUM(A2:A3)', "SUM('Synthetic Name'!E2,'Synthetic Name'!F2)")
        pairs = [('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet1.xml')]
        names = {'xl/worksheets/sheet1.xml': ('Template', 'Synthetic Name')}
        self.assertEqual(format_differences(archive(source), archive(output), pairs, names), [])
        self.assertTrue(format_differences(archive(source), archive(output.replace('!E2', '!E3')), pairs, names))
        self.assertTrue(format_differences(archive(source), archive(output), pairs))

    def test_other_sheets_external_references_and_literals_are_unchanged(self):
        formula = '''SUM(OtherTemplate!A1,'OtherTemplate'!A1,[Book]Template!A1,'[Book]Template'!A1,Other:Template!A1,"Template!A1","a""Template!A1")'''
        self.assertEqual(normalize_self_references(formula, 'Template'), formula)
        self.assertEqual(normalize_self_references("'O''Brien'!A1", "O'Brien"), '__SELF__!A1')

    def test_values_and_cached_results_may_change(self):
        updated = SHEET.replace('Example', 'Synthetic').replace('<v>12</v>', '<v>99</v>')
        self.assertEqual(worksheet_signature(SHEET), worksheet_signature(updated))

    def test_format_structure_and_formula_changes_are_detected(self):
        for old, new in [('width="18"', 'width="20"'), ('ht="24"', 'ht="25"'),
                         ('s="1"', 's="3"'), ('A2:B2', 'A2:C2'),
                         ('landscape', 'portrait'), ('SUM(A2:A3)', 'SUM(A2:A4)')]:
            with self.subTest(change=old):
                self.assertNotEqual(worksheet_signature(SHEET), worksheet_signature(SHEET.replace(old, new)))

    def test_value_type_change_preserves_format(self):
        updated = SHEET.replace(' t="inlineStr"', '').replace('<is><t>Example</t></is>', '<v>15</v>')
        self.assertEqual(worksheet_signature(SHEET), worksheet_signature(updated))

    def test_style_table_change_rejected_despite_unchanged_indices(self):
        pairs = [('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet1.xml')]
        self.assertEqual(format_differences(archive(), archive(), pairs), [])
        self.assertEqual(format_differences(archive(), archive(style='<styleSheet><fonts/></styleSheet>'), pairs),
                         ['style/theme content: xl/styles.xml'])

    def test_empty_pair_list_is_not_success(self):
        with self.assertRaises(ValueError):
            format_differences(archive(), archive(), [])

    def test_unchecked_output_sheet_is_rejected(self):
        output = archive()
        with ZipFile(output, 'a') as zipped:
            zipped.writestr('xl/worksheets/sheet2.xml', SHEET)
        with self.assertRaises(ValueError):
            format_differences(archive(), output,
                               [('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet1.xml')])


if __name__ == '__main__':
    unittest.main()
