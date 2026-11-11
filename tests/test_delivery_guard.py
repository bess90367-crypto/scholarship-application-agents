import tempfile
import unittest
from pathlib import Path
from scholarship.delivery_guard import validate_deliverable

class DeliveryGuardTests(unittest.TestCase):
    def test_missing_file_must_not_be_linked(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                validate_deliverable(Path(d) / "not-created.xlsx")

    def test_empty_file_must_not_be_linked(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "empty.xlsx"
            p.touch()
            with self.assertRaises(ValueError):
                validate_deliverable(p)

    def test_fake_extension_must_not_be_linked(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.xlsx"
            p.write_text("not an excel file")
            with self.assertRaises(ValueError):
                validate_deliverable(p)

    def test_real_workbook_can_be_linked(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "valid.xlsx"
            Workbook().save(p)
            self.assertEqual(validate_deliverable(p), p.resolve())

    def test_real_docx_can_be_linked(self):
        from docx import Document
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "valid.docx"
            Document().save(p)
            self.assertEqual(validate_deliverable(p), p.resolve())

if __name__ == "__main__":
    unittest.main()
