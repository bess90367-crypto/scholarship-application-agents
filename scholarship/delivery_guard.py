"""Fail-closed artifact validation before issuing any sandbox download link."""
from pathlib import Path
from zipfile import ZipFile, BadZipFile


def validate_deliverable(path):
    """Validate a real nonempty file and its format; return resolved path."""
    p = Path(path)
    if not p.is_file() or p.stat().st_size <= 0:
        raise ValueError("Deliverable file is missing or empty")
    suffix = p.suffix.lower()
    if suffix not in {".xlsx", ".docx"}:
        raise ValueError("Unsupported deliverable format")
    try:
        with ZipFile(p) as z:
            if z.testzip() is not None:
                raise ValueError("Corrupt OOXML archive")
            names = set(z.namelist())
            if "[Content_Types].xml" not in names:
                raise ValueError("Missing OOXML content types")
            if suffix == ".xlsx" and "xl/workbook.xml" not in names:
                raise ValueError("Missing Excel workbook")
            if suffix == ".docx" and "word/document.xml" not in names:
                raise ValueError("Missing Word document")
    except (BadZipFile, OSError) as e:
        raise ValueError("Deliverable cannot be opened") from e
    if suffix == ".xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(p, read_only=True, data_only=False)
        try:
            if not wb.sheetnames:
                raise ValueError("Excel workbook has no sheets")
        finally:
            wb.close()
    else:
        from docx import Document
        Document(p)
    return p.resolve()
