from io import BytesIO
import unittest
from zipfile import ZipFile
from scholarship.word_guard import verify_preserved_regions


def doc(blocks, style=b'synthetic-style'):
    output = BytesIO()
    with ZipFile(output, 'w') as package:
        package.writestr('word/document.xml',
                         '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                         '<w:body>' + ''.join(blocks) + '</w:body></w:document>')
        package.writestr('word/styles.xml', style)
    output.seek(0)
    return output


def paragraph(text, extra=''):
    return '<w:p>' + extra + '<w:r><w:t>' + text + '</w:t></w:r></w:p>'


class WordGuardTests(unittest.TestCase):
    def setUp(self):
        self.blocks = [paragraph('synthetic term'), paragraph('synthetic manual status 3'),
                       paragraph('synthetic manual count 5')]
        self.regions = {'manual status': ([1], [1]), 'manual count': ([2], [2])}

    def test_allowed_title_edit_keeps_manual_regions(self):
        edited = [paragraph('new term')] + self.blocks[1:]
        self.assertTrue(verify_preserved_regions(doc(self.blocks), doc(edited), self.regions,
                                                ['word/styles.xml'])['passed'])

    def test_manual_number_change_fails(self):
        edited = self.blocks[:2] + [paragraph('synthetic manual count 6')]
        self.assertFalse(verify_preserved_regions(doc(self.blocks), doc(edited), self.regions)['passed'])

    def test_manual_format_change_fails(self):
        edited = self.blocks[:2] + [paragraph('synthetic manual count 5', '<w:pPr><w:keepNext/></w:pPr>')]
        self.assertFalse(verify_preserved_regions(doc(self.blocks), doc(edited), self.regions)['passed'])

    def test_explicit_remapping_after_insertion(self):
        edited = [paragraph('new applicant')] + self.blocks
        remapped = {'manual status': ([1], [2]), 'manual count': ([2], [3])}
        self.assertTrue(verify_preserved_regions(doc(self.blocks), doc(edited), remapped)['passed'])

    def test_invalid_or_empty_regions_fail_closed(self):
        for regions in ({}, {'empty': ([], [])}, {'negative': ([-1], [2])},
                        {'outside': ([4], [2])}, {'repeat': ([1, 1], [1, 1])}):
            with self.subTest(regions=regions), self.assertRaises(ValueError):
                verify_preserved_regions(doc(self.blocks), doc(self.blocks), regions)

    def test_styles_or_missing_parts_fail(self):
        for parts in (['word/styles.xml'], ['word/header1.xml']):
            self.assertFalse(verify_preserved_regions(doc(self.blocks), doc(self.blocks, b'changed'),
                                                     self.regions, parts)['passed'])


if __name__ == '__main__':
    unittest.main()
