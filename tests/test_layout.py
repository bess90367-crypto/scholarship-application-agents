import unittest
from scholarship.layout import applicant_sheets, semester, semester_matches


class LayoutTests(unittest.TestCase):
    def test_duplicate_names_deterministic_and_identity_based(self):
        rows = [{'student_id': '0001', 'name': '合成姓名'}, {'student_id': '0002', 'name': '合成姓名'}]
        first = applicant_sheets(rows)
        self.assertEqual(first, applicant_sheets(list(reversed(rows))))
        self.assertEqual(len(set(first.values())), 2)
        self.assertEqual(set(first), {'0001', '0002'})
        self.assertTrue(all(name.startswith('合成姓名-') for name in first.values()))

    def test_reserved_invalid_case_and_long_names(self):
        rows = [{'student_id': str(i), 'name': name} for i, name in enumerate(
            ['計算模板', 'history', 'A/B', 'a?b', '長'*40, '長'*39+'名', "'測試'"])]
        names = list(applicant_sheets(rows).values())
        self.assertEqual(len({n.casefold() for n in names}), len(names))
        self.assertTrue(all(len(n) <= 31 and not any(c in n for c in '\\/*?:[]') for n in names))
        self.assertNotIn('history', {n.casefold() for n in names})
        self.assertNotIn('計算模板', names)
        self.assertIn('測試', names)

    def test_missing_or_duplicate_identity_blocks(self):
        for rows in ([{'name': '甲'}], [{'student_id': 1, 'name': '甲'}],
                     [{'student_id': '01', 'name': '甲'}, {'student_id': '01', 'name': '乙'}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError): applicant_sheets(rows)

    def test_name_whitespace_does_not_define_identity(self):
        self.assertEqual(applicant_sheets([{'student_id': '0001', 'name': '  合成姓名  '}]), {'0001': '合成姓名'})

    def test_exact_semester_component(self):
        for path in ('115-1', '/root/115-1/forms', 'root\\115-1\\forms'):
            self.assertTrue(semester_matches(path, '115-1'))
        for path in ('1115-1', '115-10', '/root/1115-1/forms', '/root/115-10/forms', 'prefix115-1', '115-1副本'):
            self.assertFalse(semester_matches(path, '115-1'))

    def test_invalid_or_missing_semester_blocks(self):
        for value in (None, '', '115', '115-3', '0115-1', 115):
            with self.subTest(value=value), self.assertRaises(ValueError): semester(value)
