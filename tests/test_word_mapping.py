import unittest
from scholarship.word_mapping import score_text, mixed_average, previous_year_cell, no_other_award


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

    def test_year_mapping(self):
        self.assertEqual([previous_year_cell(y) for y in (2, 3, 4)], ['M8', 'M9', 'M10'])
        with self.assertRaises(ValueError):
            previous_year_cell(1)

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
