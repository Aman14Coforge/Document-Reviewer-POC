# Document-Reviewer-POC

Document Reviewer POC for Compliance Rules.

## What is implemented so far

This project currently includes:

- file type detection for PDF, DOCX, and TXT files
- friendly validation messages for corrupt, unsupported, oversized, and empty-extraction cases
- text extraction from PDF, DOCX, and TXT documents
- a rule-checking helper that evaluates 13 review rules and returns a JSON-ready summary

## Project structure

- src/utilities/file_type_utils.py
  - detects file types
  - provides validation helpers and friendly error messages
- src/utilities/text_extraction_utils.py
  - extracts text from supported document formats
- src/helper/rule_checker.py
  - checks 13 compliance/rules review conditions and returns pass/fail results
- src/test.ipynb
  - notebook test area for trying the utility flow

## Quick usage

### File type and validation

```python
from src.utilities.file_type_utils import get_file_type, is_supported_file, validate_file

print(get_file_type("Data/docs/sample.docx"))
print(is_supported_file("Data/docs/sample.pdf"))
print(validate_file("Data/docs/sample.pdf", file_size_bytes=10))
```

### Extract document text

```python
from src.utilities.text_extraction_utils import extract_text

text = extract_text("Data/docs/Deployment Report_v0 - filled.docx")
print(type(text).__name__)
print(text[:300])
```

### Rule checking

```python
from helper.rule_checker import RuleChecker

result = RuleChecker("Data/docs/Deployment Report_v0 - filled.docx").evaluate()
print(result)
```

## Environment setup

To activate the local virtual environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```
