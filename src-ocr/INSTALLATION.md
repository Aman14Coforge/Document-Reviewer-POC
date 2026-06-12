# Installation Instructions - Document Extractor Chatbot

## Prerequisites Checklist ✓

- [ ] Windows/macOS/Linux system
- [ ] Python 3.8 through 3.12 installed
- [ ] Tesseract OCR installed
- [ ] Poppler installed and available in PATH
- [ ] Internet connection for package downloads

> Recommended: Use Python 3.11 or 3.12 for best compatibility. Avoid preview versions like 3.13+ or 3.15.

## Step-by-Step Installation

### 1️⃣ Install Tesseract OCR (Required)

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer: `tesseract-ocr-w64-setup-v5.x.exe`
- Default path: `C:\Program Files\Tesseract-OCR`
- ✓ Note: You'll need the installation path
- If Tesseract is not on PATH, configure `TESSERACT_PATH` in `.env`

**Windows Poppler:**
- Download Poppler for Windows from: https://poppler.freedesktop.org/
- Extract the archive and add `...\poppler-xx\Library\bin` to your PATH
- Or set `POPPLER_PATH` to the Poppler bin folder in your environment or `.env`

**macOS:**
```bash
brew install tesseract poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

### 2️⃣ Navigate to Project Directory

```bash
cd "c:\Users\L.1.Reddy\OneDrive - Coforge Limited\my workings\docuement_extracter"
```

### 3️⃣ Run Automated Setup (EASIEST WAY)

```bash
python setup.py
```

This will:
- ✓ Check Python version
- ✓ Verify Tesseract installation
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Verify everything works

### 4️⃣ Manual Setup (If Automated Setup Fails)

**Create Virtual Environment:**
```bash
# Windows
py -3.12 -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

> If `python` is a preview version like 3.15, use `py -3.12 -m venv venv`.

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

> The project now includes `pymupdf`, so PDF extraction works even if Poppler is not available.

**Configure Tesseract (Windows only, if needed):**

Preferred method: copy `.env.example` to `.env` and set `TESSERACT_PATH` there.

Example `.env` entry:
```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Configure Poppler and Tesseract via `.env`:**
- Copy `.env.example` to `.env`
- Set `POPPLER_PATH` to the Poppler `bin` folder if Poppler is not on PATH
- Set `TESSERACT_PATH` to the Tesseract executable if needed

Example `.env` entries:
```env
POPPLER_PATH=C:\poppler-xx\Library\bin
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

If you prefer not to use `.env`, the app still supports PATH-based discovery for both tools.

### 5️⃣ Run the Application

```bash
# Make sure venv is activated first!
streamlit run app.py
```

**Browser will open automatically at:** `http://localhost:8501`

---

## Troubleshooting Common Issues

### ❌ "Tesseract is not installed or found"

**Solution:**
1. Verify Tesseract is installed:
   - Windows: Check `C:\Program Files\Tesseract-OCR`
   - macOS: Run `which tesseract`
   - Linux: Run `which tesseract`

2. If installed but not found, update path in `ocr_processor.py`:
   ```python
   import pytesseract
   pytesseract.pytesseract.pytesseract_cmd = r'YOUR_TESSERACT_PATH'
   ```

### ❌ "ModuleNotFoundError: No module named..."

**Solution:**
```bash
# Make sure venv is activated
pip install -r requirements.txt
```

### ❌ Port 8501 already in use

**Solution:**
```bash
streamlit run app.py --server.port=8502
```

### ❌ Poor OCR accuracy

**Solutions:**
- Use higher quality images (300+ DPI)
- Ensure text is clearly visible
- Avoid rotated documents
- Check lighting in photos

### ❌ Out of memory error

**Solutions:**
1. Reduce `OCR_DPI` in `config.py` (from 300 to 150)
2. Process smaller PDFs
3. Close other applications
4. Increase system RAM or use 64-bit Python

---

## Quick Test After Installation

```bash
# Verify all dependencies
python -c "
import streamlit
import pytesseract
from PIL import Image
import cv2
from pdf2image import convert_from_path
print('✓ All imports successful!')
"

# Check Tesseract
python -c "
import pytesseract
print('Tesseract version:', pytesseract.get_tesseract_version())
"
```

---

## First Use Guide

1. **Upload Document**
   - Click "📤 Upload Document" 
   - Select PDF or image file
   - Supported: PDF, JPG, PNG, BMP, TIFF

2. **Extract Text**
   - Click "🔍 Extract Text"
   - Wait for processing
   - View extracted text preview

3. **Ask Questions**
   - Type question in chat box
   - Click "Send"
   - Get contextual answers

4. **Use Tools**
   - 📊 Generate Summary
   - 🔑 Extract Key Terms
   - 🗑️ Clear Chat

---

## Project Structure

```
docuement_extracter/
├── app.py                    # Main Streamlit app
├── ocr_processor.py          # OCR engine
├── chatbot.py                # Q&A chatbot
├── ui_components.py          # UI helpers
├── config.py                 # Settings
├── advanced_features.py      # LLM integration (optional)
├── setup.py                  # Setup automation
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
├── QUICK_START.md            # Quick guide
├── INSTALLATION.md           # This file
├── .env.example              # Environment template
├── .gitignore                # Git ignore
└── .streamlit/
    └── config.toml           # Streamlit config
```

---

## Key Files Explained

| File | Purpose |
|------|---------|
| `app.py` | Entry point - main Streamlit interface |
| `ocr_processor.py` | Handles OCR extraction from images/PDFs |
| `chatbot.py` | Q&A engine that searches documents |
| `ui_components.py` | Streamlit UI components and helpers |
| `config.py` | Configurable settings |
| `requirements.txt` | Python package dependencies |

---

## Getting Help

### Documentation
- **Full Guide**: [README.md](README.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Advanced Features**: See `advanced_features.py` comments

### Online Resources
- Streamlit: https://docs.streamlit.io
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Python: https://docs.python.org

### Verify Setup
Run the automated setup to verify:
```bash
python setup.py
```

---

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.8 | 3.9+ |
| RAM | 4 GB | 8 GB+ |
| Disk | 2 GB | 5 GB+ |
| Tesseract | Required | Latest |

---

## Uninstallation

To remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove venv (Windows)
rmdir /s /q venv

# Remove venv (macOS/Linux)
rm -rf venv

# Remove project folder
rm -rf docuement_extracter
```

---

## Success Checklist

- [ ] Tesseract OCR installed
- [ ] Python 3.8+ available
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Streamlit runs without errors
- [ ] Can upload a test document
- [ ] Can extract text successfully
- [ ] Can ask questions about document

---

## Next Steps

1. ✅ Complete installation
2. ✅ Run `streamlit run app.py`
3. ✅ Upload a test document (PDF or image)
4. ✅ Extract text
5. ✅ Ask questions about your document
6. ✅ Explore all features

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review README.md
3. Check Tesseract installation
4. Try automated setup: `python setup.py`

---

**Happy Extracting! 🎉**

Your Document Extractor Chatbot is ready to use. Start by uploading a document and extracting its content!
