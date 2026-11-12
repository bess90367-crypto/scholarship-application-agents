import unittest
from scholarship.word_mapping import (
    authoritative_word_score,
    derive_year_level,
    mixed_average,
    no_other_award,
    previous_year_cell,
    score_text,
    suggested_year_label,
    year_resolution_options,
)


class WordMappingTests(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(score_text('87.815'), '87.82')

    def test_full_precision_before_rounding(self):
        self.assertEqual(mixed_average('80.004', '90.005'), '85.00')

    def test_missing_not_zero(self):
        for value in (None, '', '--', 'NaN'):
            with self.assertRaises(ValueError):
                mixed_average(value, 90)
        self.assertEqual(score_text(0), '0.00')

    def test_word_score_uses_verified_calculation_not_self_report(self):
        self.assertEqual(authoritative_word_score(spreadsheet_value='92.49'), '92.49')
        self.assertEqual(authoritative_word_score(independent_value='92.486'), '92.49')
        self.assertEqual(
            authoritative_word_score(spreadsheet_value='92.49', independent_value='92.486'),
            '92.49',
        )
        with self.assertRaises(ValueError):
            authoritative_word_score(spreadsheet_value='89.46', independent_value='92.486')
        with self.assertRaises(ValueError):
            authoritative_word_score()

    def test_year_mapping(self):
        self.assertEqual([previous_year_cell(y) for y in (2, 3, 4)], ['M8', 'M9', 'M10'])
        with self.assertRaises(ValueError):
            previous_year_cell(1)

    def test_year_suggestion_comes_from_enrollment_academic_year(self):
        self.assertEqual(derive_year_level(114, 115), 2)
        self.assertEqual(suggested_year_label('碩士班', 114, 115), '碩二')
        self.assertEqual(suggested_year_label('大學部', 113, 115), '三年級')

    def test_year_conflict_returns_user_choices(self):
        result = year_resolution_options('碩士班', 114, 115, source_label='碩一')
        self.assertTrue(result['conflict'])
        self.assertEqual(result['suggested'], '碩二')
        self.assertEqual(result['options'], ['碩二', '碩一'])

    def test_duplicate_copy_not_other_award(self):
        r = {'student_id': 'SYN-A', 'scholarship': 'Synthetic award A'}
        self.assertTrue(no_other_award('SYN-A', [r, r], complete=True))

    def test_cross_award(self):
        rows = [{'student_id': 'SYN-A', 'scholarship': a} for a in ('Award A', 'Award B')]
        self.assertFalse(no_other_award('SYN-A', rows, complete=True))

    def test_incomplete_or_unresolved(self):
        rows = [{'student_id': 'SYN-A', 'scholarship': 'Award A'}]
        self.assertIsNone(no_other_award('SYN-A', rows))
        self.assertIsNone(no_other_award('SYN-A', rows, True, True))
        self.assertIsNone(no_other_award('', rows, True))
        self.assertIsNone(no_other_award('SYN-B', rows, True))


if __name__ == "__main__":
    unittest.main()
