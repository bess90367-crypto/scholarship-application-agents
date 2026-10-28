import copy
import unittest
from scholarship.core import score, validate_rank, discrepancies


def row(key, credit, grade):
    return {'id': key, 'credits': credit, 'score': grade, 'include': True, 'status': 'confirmed',
            'source': {'document_id': 'synthetic', 'page': 1, 'locator': 'row ' + key}}


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.document = {'rules': {'id': 'synthetic-policy', 'status': 'confirmed'},
                         'courses': [row('a', 3, 80), row('b', 2, 0)]}

    def test_zero_counts_in_denominator(self):
        self.assertEqual(score(self.document)['average'], '48')
        self.assertEqual(score(self.document)['credits'], '5')

    def test_missing_not_zero(self):
        self.document['courses'][1]['score'] = None
        with self.assertRaises(ValueError): score(self.document)

    def test_unknown_rule_blocks(self):
        self.document['rules']['status'] = 'unconfirmed'
        with self.assertRaises(ValueError): score(self.document)

    def test_duplicate_id_blocks(self):
        self.document['courses'].append(copy.deepcopy(self.document['courses'][0]))
        with self.assertRaises(ValueError): score(self.document)

    def test_exclusion_requires_reason(self):
        self.document['courses'][1]['include'] = False
        with self.assertRaises(ValueError): score(self.document)
        self.document['courses'][1]['exclusion_reason'] = 'synthetic excluded policy'
        self.assertEqual(score(self.document)['average'], '80')

    def test_uncertain_evidence_blocks(self):
        self.document['courses'][0]['status'] = 'uncertain'
        with self.assertRaises(ValueError): score(self.document)

    def test_invalid_numeric_inputs(self):
        for value in (True, 'NaN', 'Infinity', -1, 101):
            self.document['courses'][0]['score'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): score(self.document)

    def test_zero_credits_do_not_weight(self):
        self.document['courses'][1]['credits'] = 0
        self.assertEqual(score(self.document)['average'], '80')

    def test_rank_preserves_scope(self):
        rank = row('r', 1, 1)
        rank.update(scope='department', period='all semesters', position=2, population=40)
        self.assertEqual(validate_rank(rank)['position_fraction'], '0.05')
        del rank['period']
        with self.assertRaises(ValueError): validate_rank(rank)

    def test_rank_invalid_population(self):
        rank = row('r', 1, 1)
        rank.update(scope='class', period='term', position=2, population=1)
        with self.assertRaises(ValueError): validate_rank(rank)

    def test_discrepancy_keeps_both_values(self):
        comparison = {'field': 'average', 'application_value': 90, 'transcript_value': 85}
        self.assertEqual(discrepancies({'comparisons': [comparison]}), [comparison])


if __name__ == '__main__': unittest.main()
