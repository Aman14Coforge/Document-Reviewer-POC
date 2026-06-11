import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

ERROR_MESSAGES = {
    'file_unreadable': '⚠️ Could not read file. Please check it is not password-protected or corrupt.',
    'file_too_large': '⚠️ File is too large. Maximum supported size is 50MB.',
    'unsupported_file_type': '⚠️ Unsupported file type. Please upload PDF, DOCX, or TXT files only.',
    'rules_file_empty': '⚠️ Could not extract rules from the uploaded rules file. Please verify it contains readable text.',
    'empty_extraction': '⚠️ Document appears to be empty or image-only. Text extraction returned no content.',
}


def get_file_type(file_path):
    """
    Return the document type for a given file path.

    Returns:
        'pdf' for .pdf files
        'doc' for .doc and .docx files
        'txt' for .txt files
        'other' for any other extension
    """
    extension = Path(file_path).suffix.lower()

    if extension == '.pdf':
        return 'pdf'
    if extension in ('.doc', '.docx'):
        return 'doc'
    if extension == '.txt':
        return 'txt'
    return 'other'


def is_supported_file(file_path):
    """Return True if the path points to a supported document type."""
    return get_file_type(file_path) in ('pdf', 'doc', 'txt')


def is_pdf_or_doc(file_path):
    """Return True if the path points to a PDF or Word document."""
    return get_file_type(file_path) in ('pdf', 'doc')


def get_error_message(error_key):
    """Return the friendly message for a recognised validation error."""
    return ERROR_MESSAGES.get(error_key, '')


def validate_file(file_path, file_size_bytes=None, extracted_text=None):
    """Validate file size, type, and extraction output for friendly error handling."""
    if file_size_bytes is not None and file_size_bytes > MAX_FILE_SIZE_BYTES:
        return get_error_message('file_too_large')

    if not is_supported_file(file_path):
        return get_error_message('unsupported_file_type')

    if extracted_text is not None and not str(extracted_text).strip():
        return get_error_message('empty_extraction')

    return None


def validate_rules_file(file_path, file_size_bytes=None, extracted_text=None):
    """Validate a rules file specifically for friendly rule-extraction errors."""
    if file_size_bytes is not None and file_size_bytes > MAX_FILE_SIZE_BYTES:
        return get_error_message('file_too_large')

    if not is_supported_file(file_path):
        return get_error_message('unsupported_file_type')

    if extracted_text is not None and not str(extracted_text).strip():
        return get_error_message('rules_file_empty')

    return None
