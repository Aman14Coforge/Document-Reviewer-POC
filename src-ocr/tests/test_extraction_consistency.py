import unittest
import os
import tempfile
import shutil
import re
from importlib import import_module

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import fitz
except ImportError:
    fitz = None

try:
    import pytesseract
except Exception:
    pytesseract = None

class TestExtractionConsistency(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='test_extract_')
        if pytesseract is None:
            self.skipTest('pytesseract not available in test environment')
        ocr_mod = import_module('ocr_processor')
        # Avoid requiring Tesseract binary for this test: monkeypatch availability check
        try:
            ocr_mod.OCRProcessor._ensure_tesseract_available = lambda self: None
        except Exception:
            pass
        self.ocr = ocr_mod.OCRProcessor()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _collapse_ws(self, s: str) -> str:
        return re.sub(r"\s+", ' ', s or '').strip().lower()

    def test_docx_pdf_extract_match(self):
        if Document is None or fitz is None:
            self.skipTest('python-docx or PyMuPDF not available in test environment')

        text_paragraphs = [
            "This is a sample document for extraction consistency testing.",
            "It includes ligatures like office and ffi sequences, and smart quotes ‘like this’.",
            "Hyphenation test: hyphen-\nsplit across a line should join into one word.",
            "New paragraphs should be preserved as paragraph breaks."
        ]
        docx_path = os.path.join(self.tmpdir, 'sample.docx')
        pdf_path = os.path.join(self.tmpdir, 'sample.pdf')

        # Create DOCX
        doc = Document()
        for p in text_paragraphs:
            doc.add_paragraph(p)
        doc.save(docx_path)

        # Create simple PDF with the same text using PyMuPDF
        pdf_doc = fitz.open()
        page = pdf_doc.new_page()
        y = 72
        for p in text_paragraphs:
            page.insert_text((72, y), p, fontsize=11)
            y += 18
        pdf_doc.save(pdf_path)
        pdf_doc.close()

        # Extract using the OCRProcessor (DOCX extraction path and PDF extraction path)
        extracted_docx = self.ocr.extract_text_from_docx(docx_path)
        extracted_pdf = self.ocr.extract_text_from_pdf(pdf_path)

        # Compare normalized forms
        norm_docx = self._collapse_ws(extracted_docx)
        norm_pdf = self._collapse_ws(extracted_pdf)

        self.assertEqual(norm_docx, norm_pdf, msg=f"DOCX vs PDF normalized mismatch:\nDOCX:\n{extracted_docx}\n\nPDF:\n{extracted_pdf}")

if __name__ == '__main__':
    unittest.main()
