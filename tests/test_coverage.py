import unittest
from scholarship.coverage import batch_coverage


class CoverageTests(unittest.TestCase):
    def test_new_source_invalidates_previous_completion(self):
        files = [{'source_id': 'synthetic-a', 'page_count': 2, 'reviewed_pages': [1, 2]}]
        self.assertTrue(batch_coverage(files)['complete'])
        files.append({'source_id': 'synthetic-b', 'page_count': 3, 'reviewed_pages': []})
        self.assertEqual(batch_coverage(files)['missing_pages'], {'synthetic-b': [1, 2, 3]})

    def test_split_overlap_does_not_hide_missing_page(self):
        result = batch_coverage([{'source_id': 'synthetic', 'page_count': 4,
                                  'reviewed_pages': [1, 2, 2, 4]}])
        self.assertFalse(result['complete'])
        self.assertEqual(result['missing_pages'], {'synthetic': [3]})

    def test_invalid_inventory_rejected(self):
        for items in ([], [{'source_id': 'a', 'page_count': None}],
                      [{'source_id': 'a', 'page_count': 2, 'reviewed_pages': [3]}],
                      [{'source_id': 'a', 'page_count': 1}] * 2):
            with self.subTest(items=items), self.assertRaises(ValueError):
                batch_coverage(items)
