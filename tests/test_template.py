from io import BytesIO
import unittest
from pathlib import Path
from scholarship.core import identifier, unique_mapping
from scholarship.__main__ import template

try:
    from openpyxl import Workbook
    from openpyxl.worksheet.formula import ArrayFormula
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class MappingTests(unittest.TestCase):
    def test_identifier_preserves_leading_zeros(self):
        self.assertEqual(identifier(' 00123 '), '00123')
        with self.assertRaises(ValueError): identifier(123)

    def test_upper_lower_remain_distinct(self):
        rows = [{'name': '合成課程上', 'term': '範例'}, {'name': '合成課程下', 'term': '範例'}]
        self.assertEqual(len(unique_mapping(rows)), 2)

    def test_duplicate_mapping_rejected(self):
        rows = [{'name': '合成課程上', 'term': '範例'}, {'name': ' 合成課程上 ', 'term': '範例'}]
        with self.assertRaises(ValueError): unique_mapping(rows)

    def test_repeat_name_different_term_preserved(self):
        rows = [{'name': '合成課程', 'term': '甲'}, {'name': '合成課程', 'term': '乙'}]
        self.assertEqual(len(unique_mapping(rows)), 2)


@unittest.skipUnless(HAS_OPENPYXL, 'optional openpyxl dependency is unavailable')
class TemplateTests(unittest.TestCase):
    def test_array_formulas_numeric_types_and_dimensions(self):
        with BytesIO() as path:
            book = Workbook()
            sheet = book.active
            sheet['A1'] = 3
            sheet['A2'] = 2.5
            sheet['B1'] = '00123'
            sheet['C1'] = ArrayFormula(ref='C1:C2', text='=A1:A2*2')
            sheet.row_dimensions[1].height = 24
            sheet.column_dimensions['A'].width = 18
            book.save(path)
            path.seek(0)
            result = template(path)['sheets'][0]
            cells = {c['coordinate']: c['value'] for c in result['cells']}
            self.assertEqual(cells['C1'], {'formula': '=A1:A2*2', 'ref': 'C1:C2'})
            self.assertIsInstance(cells['A1'], int)
            self.assertEqual(cells['A2'], 2.5)
            self.assertEqual(cells['B1'], '00123')
            self.assertEqual(result['row_heights']['1'], 24)
            self.assertEqual(result['column_widths']['A'], 18)


if __name__ == '__main__': unittest.main()
