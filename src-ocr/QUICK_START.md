# Quick Start Guide - Document Extractor Chatbot

## Windows Setup (5 minutes)

### Step 1: Install Tesseract OCR
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path
3. Default path: `C:\Program Files\Tesseract-OCR`

### Step 2: Create Virtual Environment
```bash
# Recommended on Windows when multiple Python versions are installed
py -3.12 -m venv venv
venv\Scripts\activate
```

> If `python` points to preview Python 3.13+ or 3.15, use `py -3.12 -m venv venv` instead.

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Tesseract (if needed)
Edit `ocr_processor.py` and add after imports:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open at: http://localhost:8501

---

## macOS Setup (5 minutes)

### Step 1: Install Tesseract
```bash
brew install tesseract
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

---

## Linux Setup (Ubuntu/Debian) (5 minutes)

### Step 1: Install Tesseract
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

---

## First Time Usage

1. **Upload a Document**
   - Click "📤 Upload Document" in the sidebar
   - Select a PDF or image file

2. **Extract Text**
   - Click "🔍 Extract Text" button
   - Wait for processing to complete

3. **Ask Questions**
   - Type a question in the chat box
   - Click "Send" to get answers

4. **Explore Tools**
   - Generate Summary: Get document overview
   - Extract Key Terms: Find important keywords
   - Clear Chat: Start fresh

---

## Test Files

To test the application, you can use:
- Any PDF file with clear text
- Scanned images of documents
- Screenshots with readable text
- Invoice images
- Receipt images
- Contract documents

---

## Troubleshooting

### Tesseract Not Found Error
```
Verify installation path:
Windows: C:\Program Files\Tesseract-OCR
macOS: /usr/local/bin/tesseract
Linux: /usr/bin/tesseract
```

### Poor OCR Results
- Use higher resolution images (300+ DPI)
- Ensure text is clearly visible
- Avoid rotated or skewed documents
- Ensure good lighting in photos

### Port Already in Use
If port 8501 is in use:
```bash
streamlit run app.py --server.port=8502
```

### Memory Issues
- Reduce OCR_DPI in config.py
- Process large PDFs separately
- Close other applications

---

## Basic Testing Script

Create `test_app.py` to test before running:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

print("Testing Document Extractor Setup...")

# Test imports
try:
    import streamlit
    print("✓ Streamlit installed")
except ImportError:
    print("✗ Streamlit not found")
    sys.exit(1)

try:
    import pytesseract
    print("✓ Pytesseract installed")
except ImportError:
    print("✗ Pytesseract not found")
    sys.exit(1)

try:
    from PIL import Image
    print("✓ Pillow installed")
except ImportError:
    print("✗ Pillow not found")
    sys.exit(1)

try:
    import cv2
    print("✓ OpenCV installed")
except ImportError:
    print("✗ OpenCV not found")
    sys.exit(1)

try:
    from pdf2image import convert_from_path
    print("✓ pdf2image installed")
except ImportError:
    print("✗ pdf2image not found")
    sys.exit(1)

# Test Tesseract
try:
    pytesseract.get_tesseract_version()
    print("✓ Tesseract OCR accessible")
except Exception as e:
    print(f"✗ Tesseract error: {e}")
    sys.exit(1)

print("\n✅ All tests passed! Ready to run: streamlit run app.py")
```

Run test:
```bash
python test_app.py
```

---

## Common Commands

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate      # macOS/Linux

# Deactivate virtual environment
deactivate

# Run application
streamlit run app.py

# Stop application
Ctrl+C

# View Streamlit logs
streamlit logs
```

---

## Next Steps

1. ✅ Follow setup steps above
2. ✅ Run `streamlit run app.py`
3. ✅ Upload a test document
4. ✅ Extract and ask questions
5. ✅ Customize in config.py as needed

---

## Getting Help

- Check README.md for detailed documentation
- Review config.py for available settings
- Check Tesseract wiki: https://github.com/UB-Mannheim/tesseract/wiki
- Review source code comments

---

Happy extracting! 🎉
