# src folder

This folder contains the core project helpers for document review.

## Contents

- utilities/file_type_utils.py
  - file type detection and friendly validation messages
- utilities/text_extraction_utils.py
  - text extraction for PDF, DOCX, and TXT files
- helper/rule_checker.py
  - rule evaluation and JSON-ready result output

## Logging

The helper scripts use Python's standard logging module.
If you want to see diagnostic messages while running the utilities, enable logging in your application or notebook:

```python
import logging
logging.basicConfig(level=logging.INFO)
```
