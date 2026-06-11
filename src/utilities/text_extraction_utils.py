import logging
from pathlib import Path

from src.utilities.file_type_utils import get_error_message, get_file_type, validate_file

logger = logging.getLogger(__name__)


def extract_text(file_path):
    """Extract text from PDF, DOCX, or TXT files and return a friendly message on failure."""
    if not Path(file_path).exists():
        logger.warning("File not found: %s", file_path)
        return get_error_message('file_unreadable')

    file_size_bytes = Path(file_path).stat().st_size
    validation_error = validate_file(file_path, file_size_bytes=file_size_bytes)
    if validation_error:
        logger.warning("Validation failed for %s: %s", file_path, validation_error)
        return validation_error

    file_type = get_file_type(file_path)

    try:
        if file_type == 'pdf':
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                text = '\n'.join(
                    page.extract_text() or ''
                    for page in pdf.pages
                    if (page.extract_text() or '').strip()
                )
        elif file_type == 'doc':
            from docx import Document
            from docx.table import Table
            from docx.text.paragraph import Paragraph

            doc = Document(file_path)
            full_text = []

            for element in doc.element.body:
                if element.tag.endswith('p'):
                    paragraph = Paragraph(element, doc)
                    if paragraph.text.strip():
                        full_text.append(paragraph.text)
                elif element.tag.endswith('tbl'):
                    table = Table(element, doc)
                    for row in table.rows:
                        row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_text:
                            full_text.append('\t|\t'.join(row_text))

            text = '\n'.join(full_text)
        elif file_type == 'txt':
            text = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        else:
            return get_error_message('unsupported_file_type')

        if not text.strip():
            return get_error_message('empty_extraction')

        return text

    except Exception as exc:
        logger.exception("Extraction failed for %s", file_path)
        return get_error_message('file_unreadable')
