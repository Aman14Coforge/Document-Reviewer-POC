"""
OCR Processor Module - Handles text extraction from images and PDFs
"""

import os
import platform
import shutil
import pytesseract
from pytesseract import TesseractNotFoundError
from pytesseract import pytesseract as pytesseract_core
from PIL import Image, ExifTags
import cv2
import numpy as np
from pdf2image import convert_from_path
from pdf2image import exceptions as pdf2image_exceptions
import logging
import config
from datetime import datetime

try:
    from docx import Document
except ImportError:
    Document = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Processes images and PDFs to extract text using OCR
    """
    
    def __init__(self):
        """Initialize OCR processor"""
        self.logger = logger
        self._configure_tesseract()
        self._ensure_tesseract_available()

    def _configure_tesseract(self):
        """Configure pytesseract with a valid Tesseract executable."""
        if config.TESSERACT_PATH:
            if os.path.isfile(config.TESSERACT_PATH):
                pytesseract_core.tesseract_cmd = config.TESSERACT_PATH
                self.logger.info(f"Using TESSERACT_PATH from config: {config.TESSERACT_PATH}")
                return
            self.logger.warning(
                f"TESSERACT_PATH is configured but the executable was not found at: {config.TESSERACT_PATH}"
            )

        candidate = self._find_tesseract_executable()
        if candidate:
            pytesseract_core.tesseract_cmd = candidate
            self.logger.info(f"Found Tesseract executable: {candidate}")
        else:
            self.logger.info("No Tesseract executable found in PATH or default locations.")

    def _find_tesseract_executable(self):
        """Try to locate the Tesseract executable on the local machine."""
        exe_name = "tesseract.exe" if platform.system() == "Windows" else "tesseract"

        # Check PATH first
        found = shutil.which(exe_name)
        if found:
            return found

        # Windows default install locations
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files\Tesseract\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract\tesseract.exe",
            ]
            for path in paths:
                if os.path.isfile(path):
                    return path

        return None

    def _ensure_tesseract_available(self):
        """Ensure Tesseract OCR is installed and accessible."""
        try:
            pytesseract_core.get_tesseract_version()
            self.logger.info("Tesseract OCR is available.")
        except TesseractNotFoundError as e:
            message = (
                "Tesseract OCR is not installed or not available in your PATH. "
                "On Windows, install Tesseract from the official installer and set "
                "TESSERACT_PATH in your .env file if it is not already on PATH. "
                "For example: C:\\Program Files\\Tesseract-OCR\\tesseract.exe. "
                "See README for installation instructions."
            )
            self.logger.error(message)
            raise RuntimeError(message) from e
        except Exception as e:
            message = f"Unexpected Tesseract error: {e}"
            self.logger.error(message)
            raise RuntimeError(message) from e

    def _format_exif_datetime(self, value):
        if isinstance(value, str) and ":" in value:
            try:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").isoformat()
            except ValueError:
                return value
        return value

    def _get_file_metadata(self, file_path):
        try:
            stats = os.stat(file_path)
            return {
                "file_name": os.path.basename(file_path),
                "file_size_bytes": stats.st_size,
                "created_time": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "extension": os.path.splitext(file_path)[1].lower(),
            }
        except Exception as e:
            return {"error": f"File metadata read error: {e}"}

    def _get_image_metadata(self, image_path):
        metadata = {}
        try:
            with Image.open(image_path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["size"] = img.size
                metadata["info"] = {k: str(v) for k, v in img.info.items()}
                exif = getattr(img, "_getexif", lambda: None)()
                if exif:
                    exif_data = {}
                    for tag, value in exif.items():
                        decoded = ExifTags.TAGS.get(tag, tag)
                        if isinstance(value, bytes):
                            try:
                                value = value.decode(errors="ignore")
                            except Exception:
                                value = str(value)
                        if decoded in {"DateTime", "DateTimeOriginal", "DateTimeDigitized"}:
                            value = self._format_exif_datetime(value)
                        exif_data[decoded] = value
                    metadata["exif"] = exif_data
        except Exception as e:
            metadata["error"] = f"Image metadata read error: {e}"
        return metadata

    def _get_pdf_metadata(self, pdf_path):
        try:
            import fitz
        except ImportError as e:
            return {"error": "PyMuPDF is not installed for PDF metadata extraction."}

        try:
            doc = fitz.open(pdf_path)
            metadata = {k: v for k, v in doc.metadata.items() if v is not None}
            metadata["page_count"] = doc.page_count
            return metadata
        except Exception as e:
            return {"error": f"PDF metadata read error: {e}"}

    def _get_docx_metadata(self, docx_path):
        if Document is None:
            return {"error": "python-docx is required for DOCX metadata extraction."}

        try:
            doc = Document(docx_path)
            props = doc.core_properties
            metadata = {}
            for attr in [
                "title",
                "subject",
                "creator",
                "author",
                "keywords",
                "description",
                "last_modified_by",
                "revision",
                "created",
                "modified",
                "category",
                "comments",
                "content_status",
                "language",
            ]:
                value = getattr(props, attr, None)
                if value is not None and value != "":
                    metadata[attr] = value.isoformat() if isinstance(value, datetime) else str(value)
            return metadata
        except Exception as e:
            return {"error": f"DOCX metadata read error: {e}"}

    def extract_metadata(self, file_path):
        metadata = self._get_file_metadata(file_path)
        suffix = os.path.splitext(file_path)[1].lower()

        if suffix == ".pdf":
            metadata["document"] = self._get_pdf_metadata(file_path)
        elif suffix == ".docx":
            metadata["document"] = self._get_docx_metadata(file_path)
        elif suffix in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
            metadata["document"] = self._get_image_metadata(file_path)
        else:
            metadata["document"] = {"note": "No format-specific metadata available."}

        return metadata
    
    def preprocess_image(self, image_path):
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed PIL Image
        """
        # Read image using OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply thresholding for better contrast
        _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)
        
        # Convert back to PIL Image
        pil_image = Image.fromarray(thresh)
        
        return pil_image
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        try:
            self.logger.info(f"Extracting text from image: {image_path}")
            
            self._ensure_tesseract_available()
            
            # Preprocess the image
            processed_image = self.preprocess_image(image_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, lang=config.OCR_LANGUAGE)
            
            normalized_text = self._normalize_text(text)
            self.logger.info(f"Successfully extracted {len(normalized_text)} characters from image")
            return normalized_text
        
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {str(e)}")
            raise

    def _normalize_text(self, text: str) -> str:
        """
        Normalize extracted text for consistent compliance evaluation.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text with consistent formatting
        """
        import re
        import unicodedata

        if not text:
            return ""

        # Remove common page markers and metadata-like lines
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines
            if line and not line.strip().startswith('---') and not line.strip().startswith('Page')
        ]
        s = '\n'.join(cleaned_lines)

        # Unicode normalization
        s = unicodedata.normalize('NFKC', s)

        # Remove soft hyphens and zero-width spaces
        s = s.replace('\u00AD', '')
        s = s.replace('\u200B', '')

        # Replace non-breaking spaces with normal spaces
        s = s.replace('\u00A0', ' ')

        # Common ligatures and special characters mapping
        ligatures = {
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬀ': 'ff',
            'ﬃ': 'ffi',
            'ﬄ': 'ffl',
        }
        for k, v in ligatures.items():
            s = s.replace(k, v)

        # Normalize smart quotes and dashes to ascii equivalents
        replacements = {
            '“': '"', '”': '"', '‘': "'", '’': "'",
            '–': '-', '—': '-', '•': '-', '\u2022': '-', '\u00B7': "'", '·': "'",
        }
        for k, v in replacements.items():
            s = s.replace(k, v)

        # Fix hyphenation that breaks words across lines: 'word-\nnext' -> 'wordnext'
        s = re.sub(r"(\w)-\n(\w)", r"\1\2", s)

        # Mark paragraph breaks: collapse 3+ newlines to two
        s = re.sub(r"\n{3,}", "\n\n", s)

        # Replace single newlines (within paragraphs) with spaces, preserve double newlines
        s = re.sub(r"(?<!\n)\n(?!\n)", ' ', s)

        # Collapse multiple spaces
        s = re.sub(r"[ \t]{2,}", ' ', s)

        # Trim leading/trailing whitespace on each paragraph and overall
        paragraphs = [p.strip() for p in s.split('\n\n') if p.strip()]
        normalized = '\n\n'.join(paragraphs)

        return normalized.strip()

    def extract_text_from_txt(self, txt_path):
        """
        Extract text from a TXT file.

        Args:
            txt_path: Path to the TXT file

        Returns:
            Extracted text as string
        """
        try:
            self.logger.info(f"Extracting text from TXT: {txt_path}")
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            normalized_text = self._normalize_text(text)
            self.logger.info(f"Successfully extracted {len(normalized_text)} characters from TXT")
            return normalized_text
        except Exception as e:
            self.logger.error(f"Error extracting text from TXT: {str(e)}")
            raise

    def extract_text_from_docx(self, docx_path):
        """
        Extract text from a DOCX file
        
        Args:
            docx_path: Path to the DOCX file
            
        Returns:
            Extracted text as string
        """
        if Document is None:
            raise RuntimeError("python-docx is required for DOCX extraction. Install it with `pip install python-docx`.")

        try:
            self.logger.info(f"Extracting text from DOCX: {docx_path}")
            doc = Document(docx_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = "\n".join(paragraphs)
            normalized_text = self._normalize_text(text)
            self.logger.info(f"Successfully extracted {len(normalized_text)} characters from DOCX")
            return normalized_text
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path, dpi=300):
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            dpi: DPI for PDF conversion (higher = better quality but slower)
            
        Returns:
            Extracted text as string
        """
        try:
            self.logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Convert PDF pages to images using Poppler
            poppler_kw = {"poppler_path": config.POPPLER_PATH} if config.POPPLER_PATH else {}
            images = convert_from_path(pdf_path, dpi=dpi, **poppler_kw)
            
            return self._ocr_images_from_pages(images)
        
        except (
            OSError,
            pdf2image_exceptions.PDFInfoNotInstalledError,
            pdf2image_exceptions.PDFPageCountError,
            pdf2image_exceptions.PopplerNotInstalledError,
            pdf2image_exceptions.PDFSyntaxError,
        ) as e:
            self.logger.warning(
                "Poppler conversion failed or PDF info could not be read. Attempting PyMuPDF fallback for PDF extraction."
            )
            try:
                return self._extract_text_from_pdf_with_pymupdf(pdf_path, dpi)
            except Exception as fallback_exc:
                error_message = (
                    "Unable to process PDF. Poppler is not available and PyMuPDF fallback failed. "
                    "Install Poppler or add PyMuPDF with `pip install pymupdf`."
                )
                self.logger.error(f"{error_message} - {str(fallback_exc)}")
                raise RuntimeError(error_message) from fallback_exc
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _ocr_images_from_pages(self, images):
        """Convert PIL page images to OCR text."""
        all_text = ""
        import os

        for idx, image in enumerate(images):
            self.logger.info(f"Processing page {idx + 1} of {len(images)}")
            img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            temp_image_path = f"temp_page_{idx}.png"
            cv2.imwrite(temp_image_path, img_array)

            processed_image = self.preprocess_image(temp_image_path)
            self._ensure_tesseract_available()
            text = pytesseract.image_to_string(processed_image, lang=config.OCR_LANGUAGE)
            all_text += f"{text}\n"

            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

        normalized_text = self._normalize_text(all_text)
        self.logger.info(f"Successfully extracted {len(normalized_text)} characters from PDF")
        return normalized_text

    def _extract_text_from_pdf_with_pymupdf(self, pdf_path, dpi=300):
        """Fallback PDF extraction using PyMuPDF when Poppler is unavailable."""
        try:
            import fitz
        except ImportError as e:
            raise RuntimeError("PyMuPDF is not installed.") from e

        self.logger.info("Using PyMuPDF fallback for PDF extraction")
        doc = fitz.open(pdf_path)
        all_text = ""
        import os

        for page_num, page in enumerate(doc):
            self.logger.info(f"Processing page {page_num + 1} of {len(doc)} with PyMuPDF")
            page_text = page.get_text("text")
            if page_text.strip():
                all_text += f"{page_text}\n"
                continue

            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            temp_image_path = f"temp_page_fitz_{page_num}.png"
            image.save(temp_image_path)

            processed_image = self.preprocess_image(temp_image_path)
            self._ensure_tesseract_available()
            text = pytesseract.image_to_string(processed_image, lang=config.OCR_LANGUAGE)
            all_text += f"{text}\n"

            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

        normalized_text = self._normalize_text(all_text)
        self.logger.info(f"Successfully extracted {len(normalized_text)} characters from PDF using PyMuPDF")
        return normalized_text
    
    def extract_text_from_directory(self, directory_path):
        """
        Extract text from all image files in a directory
        
        Args:
            directory_path: Path to directory containing images
            
        Returns:
            Dictionary with filename as key and extracted text as value
        """
        import os
        
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        results = {}
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in supported_formats:
                try:
                    # Validate file size (max 50MB)
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if file_size_mb > 50:
                        self.logger.warning(f"File {filename} exceeds 50MB limit ({file_size_mb:.1f}MB), skipping")
                        results[filename] = "Error: File too large (max 50MB)"
                        continue
                    
                    text = self.extract_text_from_image(file_path)
                    results[filename] = text
                except Exception as e:
                    self.logger.error(f"Failed to process {filename}: {str(e)}")
                    results[filename] = f"Error: {str(e)}"
        
        return results
    
    def validate_file(self, file_path, max_size_mb=50):
        """
        Validate file before processing.
        
        Args:
            file_path: Path to file to validate
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"
        
        supported_formats = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        extension = os.path.splitext(file_path)[1].lower()
        if extension not in supported_formats:
            return False, f"Unsupported file format: {extension}"
        
        return True, ""
    
    def validate_extractable(self, file_path, min_text_chars=100, min_image_dim=800, blur_threshold=100.0):
        """
        Perform heuristic checks to determine whether a document is suitable for text extraction.

        Returns:
            Tuple (is_extractable: bool, message: str, details: dict)
        """
        details = {}
        extension = os.path.splitext(file_path)[1].lower()

        # DOCX: check for presence of textual paragraphs
        if extension == ".docx":
            if Document is None:
                return False, "python-docx not available to validate DOCX content.", {"reason": "missing_python_docx"}
            try:
                doc = Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
                details["paragraph_count"] = len(paragraphs)
                if len(paragraphs) == 0:
                    return False, "DOCX contains no textual paragraphs; may not be extractable.", details
                return True, "DOCX contains textual content suitable for extraction.", details
            except Exception as e:
                return False, f"Error reading DOCX: {e}", {"error": str(e)}

        # Image files: check resolution and blurriness
        if extension in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
            try:
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    return False, "Image could not be opened or is corrupted.", {"reason": "invalid_image"}

                h, w = img.shape[:2]
                details["width"] = w
                details["height"] = h

                # Blur detection (variance of Laplacian)
                fm = cv2.Laplacian(img, cv2.CV_64F).var()
                details["laplacian_variance"] = float(fm)
                if fm < blur_threshold:
                    return False, f"Image appears blurry (laplacian variance={fm:.1f}); OCR may fail.", details

                if w < min_image_dim or h < min_image_dim:
                    return False, f"Image resolution is low ({w}x{h}); consider higher resolution.", details

                return True, "Image looks suitable for OCR extraction.", details
            except Exception as e:
                return False, f"Error validating image: {e}", {"error": str(e)}

        # TXT: simple readable text validation
        if extension == ".txt":
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                details["char_count"] = len(content)
                if not content:
                    return False, "TXT file appears empty or unreadable.", details
                return True, "TXT file contains readable text.", details
            except Exception as e:
                return False, f"Error reading TXT: {e}", {"error": str(e)}

        # PDF: try to detect if text is present or pages are image-only
        if extension == ".pdf":
            try:
                try:
                    import fitz
                except Exception:
                    return False, "PyMuPDF not installed to validate PDF content.", {"reason": "missing_pymupdf"}

                doc = fitz.open(file_path)
                if doc.is_encrypted:
                    return False, "PDF is encrypted; cannot extract without a password.", {"encrypted": True}

                page_count = doc.page_count
                details["page_count"] = page_count
                text_chars = 0
                image_pages = 0
                for page in doc:
                    page_text = page.get_text("text")
                    if page_text and page_text.strip():
                        text_chars += len(page_text.strip())
                    else:
                        image_pages += 1

                details["text_characters"] = text_chars
                details["image_pages"] = image_pages

                # If there's sufficient text, treat as extractable
                if text_chars >= min_text_chars:
                    return True, "PDF contains selectable text suitable for extraction.", details

                # If many pages are images, check resolution of first image
                if image_pages > 0:
                    # examine first image page
                    for page_num, page in enumerate(doc):
                        page_text = page.get_text("text")
                        if not page_text or not page_text.strip():
                            pix = page.get_pixmap()
                            w, h = pix.width, pix.height
                            details["sample_image_width"] = w
                            details["sample_image_height"] = h
                            if w < min_image_dim or h < min_image_dim:
                                return False, f"PDF image pages are low resolution ({w}x{h}); OCR may fail.", details
                            # quick pass: image pages appear acceptable
                            return True, "PDF pages are image-based but resolution looks sufficient for OCR.", details

                # Fallback: insufficient text but no obvious images
                return False, "PDF does not contain enough selectable text; OCR may be required.", details
            except Exception as e:
                return False, f"Error validating PDF: {e}", {"error": str(e)}

        # Unknown/unsupported extension reached earlier in validate_file, but handle defensively
        return False, f"Cannot determine extractability for file type: {extension}", {"extension": extension}
    def get_processing_stats(self):
        """Get current processing statistics."""
        return {
            "tesseract_available": pytesseract_core.tesseract_cmd is not None,
            "tesseract_path": pytesseract_core.tesseract_cmd,
            "ocr_language": config.OCR_LANGUAGE,
            "ocr_dpi": config.OCR_DPI
        }
