import unittest
from scholarship.layout import (
    applicant_sheets,
    semester,
    semester_from_request,
    semester_matches,
    select_semester_folder,
)


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

    def test_extract_semester_from_short_request(self):
        self.assertEqual(semester_from_request('請整理 115-1 的獎學金申請資料'), '115-1')
        self.assertEqual(semester_from_request('麻煩整理115-2獎學金申請'), '115-2')

    def test_request_requires_one_unambiguous_semester(self):
        for value in ('請整理獎學金資料', '整理 115-1 與 115-2', '整理 1115-1 資料'):
            with self.subTest(value=value), self.assertRaises(ValueError): semester_from_request(value)

    def test_canonical_semester_folder_names(self):
        for path in (
            '115-1',
            '/root/115-1/forms',
            'root\\115-1\\forms',
            '115-1獎學金申請資料',
            '/root/115-1獎學金申請資料/forms',
        ):
            self.assertTrue(semester_matches(path, '115-1'))

        for path in (
            '1115-1',
            '115-10',
            '/root/1115-1/forms',
            '/root/115-10/forms',
            'prefix115-1',
            '115-1副本',
            '115-1獎學金申請資料副本',
            '115-1其他資料',
        ):
            self.assertFalse(semester_matches(path, '115-1'))

    def test_select_unique_semester_folder(self):
        paths = ['/private/root/114-2獎學金申請資料', '/private/root/115-1獎學金申請資料', '/private/root/115-2獎學金申請資料']
        self.assertEqual(
            select_semester_folder(paths, '115-1'),
            '/private/root/115-1獎學金申請資料',
        )
        with self.assertRaises(ValueError):
            select_semester_folder(['/a/115-1', '/b/115-1獎學金申請資料'], '115-1')
        with self.assertRaises(ValueError):
            select_semester_folder(['/a/114-2獎學金申請資料'], '115-1')

    def test_invalid_or_missing_semester_blocks(self):
        for value in (None, '', '115', '115-3', '0115-1', 115):
            with self.subTest(value=value), self.assertRaises(ValueError): semester(value)


if __name__ == '__main__': unittest.main()
