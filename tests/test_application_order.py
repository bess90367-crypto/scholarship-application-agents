import unittest
from scholarship.application_order import ordered_applications


class ApplicationOrderTests(unittest.TestCase):
    def row(self, number, status='confirmed'):
        return {'application_number': number, 'number_status': status}

    def test_numeric_order_and_blanks_last(self):
        rows=[self.row('', 'blank'), self.row('10'), self.row('2'), self.row('1')]
        self.assertEqual([r['application_number'] for r in ordered_applications(rows)], ['1','2','10',''])

    def test_preserve_original_and_gaps(self):
        rows=[self.row('０７'), self.row('003')]
        self.assertEqual([r['application_number'] for r in ordered_applications(rows)], ['003','０７'])

    def test_stable_ties_and_blanks(self):
        rows=[dict(self.row('', 'blank'), tag='a'), dict(self.row('', 'blank'), tag='b')]
        self.assertEqual(ordered_applications(rows),rows)
        rows=[dict(self.row('2'),tag='a'),dict(self.row('2'),tag='b')]
        self.assertEqual(ordered_applications(rows),rows)

    def test_missing_is_not_confirmed_blank(self):
        for row in ({},self.row(None),self.row('?', 'uncertain'),self.row('A1'),self.row('1','blank')):
            with self.assertRaises(ValueError):ordered_applications([row])
