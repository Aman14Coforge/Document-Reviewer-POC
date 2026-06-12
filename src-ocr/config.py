"""
Configuration Module - Application settings and constants
"""

import os
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Application Settings
APP_NAME = "Document Extractor Chatbot"
APP_VERSION = "1.0.0"
AUTHOR = "Your Name"

# File Settings
UPLOAD_FOLDER = Path("uploads")
TEMP_FOLDER = Path("temp_upload")
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

# OCR Settings
OCR_DPI = int(os.getenv("OCR_DPI", 300))  # DPI for PDF conversion
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")  # Tesseract language
PREPROCESS_ENABLED = True
POPPLER_PATH = os.getenv("POPPLER_PATH", "").strip().strip('"').strip("'")  # Optional Poppler bin path for Windows
if POPPLER_PATH and Path(POPPLER_PATH).is_dir():
    POPPLER_PATH = str(Path(POPPLER_PATH) / "bin")

TESSERACT_PATH = os.getenv("TESSERACT_PATH", "").strip().strip('"').strip("'")  # Optional Tesseract executable path for Windows
if TESSERACT_PATH:
    tesseract_path_obj = Path(TESSERACT_PATH)
    if tesseract_path_obj.is_dir():
        TESSERACT_PATH = str(tesseract_path_obj / ("tesseract.exe" if platform.system() == "Windows" else "tesseract"))

# Chatbot Settings
MAX_CONTEXT_LENGTH = 2000
NUM_RELEVANT_PASSAGES = 3
SUMMARY_SENTENCES = 3
KEY_TERMS_COUNT = 10

# UI Settings
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
THEME = "light"

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)

# Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
