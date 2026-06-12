# Document Extractor Chatbot 📄

A Streamlit-based application that uses OCR (Optical Character Recognition) to extract text from documents and provides an interactive chatbot interface to ask questions about the extracted content.

## Features ✨

- **📸 Multi-Format Support**: Extract text from PDF files and images (JPG, PNG, BMP, TIFF)
- **🔍 Advanced OCR**: Uses Tesseract OCR with image preprocessing for better accuracy
- **💬 Interactive Chatbot**: Ask questions about extracted documents with intelligent Q&A
- **📊 Document Analysis**: View statistics, summaries, and key terms from documents
- **🎯 Smart Context Matching**: Finds relevant passages in documents to answer questions
- **📱 User-Friendly Interface**: Clean, intuitive Streamlit UI
- **🚀 Fast Processing**: Efficient text extraction and indexing

## Project Structure 📁

```
document_extractor/
├── app.py                 # Main Streamlit application
├── ocr_processor.py       # OCR processing and text extraction
├── chatbot.py             # Chatbot logic and Q&A engine
├── ui_components.py       # Streamlit UI helper functions
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Prerequisites 📋

Before running the application, ensure you have:

1. **Python 3.8 to 3.12** installed
2. **Tesseract OCR** installed on your system (required by pytesseract)
3. **Poppler** installed on your system (required by pdf2image for PDF conversion)
4. **Git** (optional, for version control)

> Note: Python 3.15 and preview installations may not have compatible Streamlit or NumPy wheels yet. If `streamlit` is missing or `numpy` fails to build, recreate the virtual environment with a supported interpreter:
> `py -3.12 -m venv venv`
> then install dependencies with:
> `venv\Scripts\python.exe -m pip install -r requirements.txt`

### Installing Tesseract OCR

#### Windows:
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run `tesseract-ocr-w64-setup-v5.x.exe`
3. During installation, note the install path, usually `C:\Program Files\Tesseract-OCR`
4. If Tesseract is not on PATH, set `TESSERACT_PATH` in `.env` instead of editing code directly

#### Poppler (Windows):
1. Download from: https://poppler.freedesktop.org/
2. Extract the zip archive to a folder such as `C:\poppler-xx\`
3. Add `C:\poppler-xx\Library\bin` to your PATH
4. If you prefer, set `POPPLER_PATH` in the environment or `.env` file to the Poppler `bin` folder

#### Fallback with PyMuPDF:
If Poppler is not installed, the app now uses PyMuPDF as a fallback to extract text from PDFs. This avoids repeated failures for most PDFs.

#### Configure `.env` support:
- The app loads `.env` automatically via `python-dotenv`
- Copy `.env.example` to `.env`
- Set `TESSERACT_PATH` to your Tesseract executable if it is not on PATH
- Set `POPPLER_PATH` to the Poppler `bin` folder if Poppler is not on PATH

Example `.env` entries:
```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler-xx\Library\bin
```

#### macOS:
```bash
brew install tesseract poppler
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

## Installation ⚙️

### 1. Clone or Download the Project
```bash
cd document_extractor
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Tesseract Path (Windows Only)

Preferred method: copy `.env.example` to `.env` and set the Tesseract path there.

Example `.env` entry:
```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is already on PATH, no additional configuration is needed.

## Running the Application 🚀

If `streamlit` is not available globally, use the local virtual environment instead.

```powershell
# Activate the project venv first (Windows)
venv\Scripts\activate

# Then start Streamlit
python -m streamlit run app.py
```

Or use one of the bundled launchers:

```powershell
run_app.bat
# or
.\run_app.ps1
```

The application will open in your default browser at `http://localhost:8501`

## Usage Guide 📖

### 1. Upload a Document
- Click "Upload Document" in the left sidebar
- Select a PDF file or image (JPG, PNG, BMP, TIFF)
- Supported file types will be highlighted

### 2. Extract Text
- Click the "🔍 Extract Text" button
- Wait for the OCR processing to complete
- The extracted text will be displayed in the preview area

### 3. Ask Questions
- In the chat area, type your question about the document
- Click "Send" or press Enter
- The chatbot will search the document and provide relevant answers
- Your conversation history is maintained throughout the session

### 4. Document Tools
- **Generate Summary**: Get a brief summary of the document
- **Extract Key Terms**: Identify important terms from the document
- **Clear Chat**: Reset the conversation and start over

## API Reference 🔧

### OCRProcessor Class

```python
from ocr_processor import OCRProcessor

processor = OCRProcessor()

# Extract text from image
text = processor.extract_text_from_image("path/to/image.jpg")

# Extract text from PDF
text = processor.extract_text_from_pdf("path/to/document.pdf")

# Process entire directory
results = processor.extract_text_from_directory("path/to/images/")
```

### DocumentChatbot Class

```python
from chatbot import DocumentChatbot

# Initialize with extracted text
chatbot = DocumentChatbot(extracted_text)

# Get response to a query
response = chatbot.generate_response("What is the main topic?")

# Generate summary
summary = chatbot.get_summary()

# Extract key terms
key_terms = chatbot.get_key_terms()

# Get conversation history
history = chatbot.get_history()

# Clear history
chatbot.clear_history()
```

## Configuration 🔧

Edit `config.py` to customize:

```python
OCR_DPI = 300                  # DPI for PDF conversion
OCR_LANGUAGE = 'eng'           # Tesseract language
MAX_CONTEXT_LENGTH = 2000      # Max context for chatbot
NUM_RELEVANT_PASSAGES = 3      # Number of passages to retrieve
SUMMARY_SENTENCES = 3          # Sentences in summary
KEY_TERMS_COUNT = 10           # Number of key terms to extract
```
### OpenAI LLM Integration

To enable enhanced responses from OpenAI, set `OPENAI_API_KEY` in your environment or `.env` file. When configured, the app will use the OpenAI chat completion API to answer questions based on the extracted document context.
## Supported Languages 🌍

Tesseract supports multiple languages. To use different languages, update `OCR_LANGUAGE` in `config.py`:

- `'eng'` - English
- `'fra'` - French
- `'deu'` - German
- `'spa'` - Spanish
- `'chi_sim'` - Simplified Chinese
- `'jpn'` - Japanese

For additional languages, download language packs from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki/Downloads-for-different-OS).

## Performance Tips 💡

1. **Image Quality**: Use high-resolution, well-lit images for better OCR accuracy
2. **Preprocessing**: The application automatically preprocesses images for better accuracy
3. **PDF DPI**: Increase `OCR_DPI` for better quality (default: 300) - higher values take longer
4. **Memory**: Large PDFs may consume significant memory; process them in batches if needed

## Troubleshooting 🐛

### Issue: "Tesseract is not installed or found"
**Solution**: 
- Ensure Tesseract-OCR is installed (see Prerequisites)
- Update the pytesseract path in `ocr_processor.py`

### Issue: Poor OCR accuracy
**Solution**:
- Use higher quality images
- Increase `OCR_DPI` in config.py
- Ensure text is clearly visible and not rotated

### Issue: Application runs slowly
**Solution**:
- Reduce PDF DPI in config.py
- Close other applications
- Use smaller file sizes

### Issue: Out of memory error
**Solution**:
- Reduce `OCR_DPI`
- Process large PDFs in smaller batches
- Close other applications

## Future Enhancements 🔮

Potential features to add:
- [ ] Integration with GPT/LLM for better Q&A
- [ ] Document comparison and highlighting
- [ ] Multi-language support with language detection
- [ ] Export extracted text to various formats (DOCX, TXT, etc.)
- [ ] Search and highlight functionality
- [ ] Document annotation and notes
- [ ] Batch processing capability
- [ ] Database integration for document storage
- [ ] Web deployment support

## Dependencies 📦

See `requirements.txt` for complete list:
- **streamlit**: Web UI framework
- **pytesseract**: Python wrapper for Tesseract OCR
- **pdf2image**: PDF to image conversion
- **Pillow**: Image processing
- **opencv-python**: Computer vision library
- **numpy**: Numerical computing

## License 📄

This project is provided as-is for educational and personal use.

## Support 💬

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review the provided examples
3. Check OCR and Tesseract documentation

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests
- Improve documentation

## Changelog 📝

### Version 1.0.0
- Initial release
- OCR text extraction from images and PDFs
- Interactive chatbot interface
- Document analysis tools
- Streamlit UI

---

**Happy Extracting!** 🎉

For more information about Tesseract OCR, visit: https://github.com/UB-Mannheim/tesseract/wiki
