"""
Rules dataset for Document Extractor Chatbot

Each rule is a dictionary with the following keys:
- id: Rule identifier
- title: Short rule title
- status: PASS/FAIL
- severity: Severity level
- violation: Violation flag or short note (optional)
- evidence: Evidence or notes (optional)
"""

import os
import re


def normalize_text_for_compliance(text: str) -> str:
    """
    Normalize text for consistent compliance evaluation.
    Handles formatting inconsistencies across PDF, DOCX, and image extractions.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Normalized text with consistent formatting
    """
    if not text:
        return ""
    
    # Remove page markers and metadata lines first
    lines = text.split('\n')
    cleaned_lines = [
        line for line in lines 
        if not line.strip().startswith('---') and 
           not line.strip().lower().startswith('page') and
           line.strip()
    ]
    
    # Join lines and convert to lowercase
    normalized = '\n'.join(cleaned_lines).lower()
    
    # Remove extra whitespace and normalize newlines
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters that don't affect compliance (but keep hyphens in numbers)
    # Keep: alphanumeric, spaces, hyphens, @ symbols, periods, commas, parentheses
    normalized = re.sub(r'[^\w\s\-@.,():/]', '', normalized)
    
    return normalized.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace variations in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ ]+', ' ', text)
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\n+', '\n', text)
    
    # Strip leading/trailing whitespace
    return text.strip()


def normalize_special_characters(text: str) -> str:
    """
    Normalize special characters and symbols for consistency.
    Maps common variations to standard forms.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized special characters
    """
    if not text:
        return ""
    
    # Map copyright variations
    text = re.sub(r'©', 'copyright', text)
    text = re.sub(r'\(c\)', 'copyright', text, flags=re.IGNORECASE)
    text = re.sub(r'&copy;', 'copyright', text)
    
    # Map registered trademark variations
    text = re.sub(r'®', 'registered', text)
    text = re.sub(r'\(r\)', 'registered', text, flags=re.IGNORECASE)
    text = re.sub(r'&reg;', 'registered', text)
    
    # Map trademark variations
    text = re.sub(r'™', 'trademark', text)
    text = re.sub(r'\(tm\)', 'trademark', text, flags=re.IGNORECASE)
    text = re.sub(r'&trade;', 'trademark', text)
    
    # Map degree symbol
    text = text.replace('°', 'degrees')
    text = re.sub(r'\(deg\)', 'degrees', text, flags=re.IGNORECASE)
    
    # Normalize quotes
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    
    # Normalize dashes
    text = re.sub(r'[–—]', '-', text)
    
    return text


def normalize_abbreviations(text: str) -> str:
    """
    Expand or normalize common abbreviations for compliance matching.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized abbreviations
    """
    if not text:
        return ""
    
    text = text.lower()
    
    # Expand common compliance-related abbreviations
    abbreviations = {
        r'\bgdpr\b': 'general data protection regulation',
        r'\bhipaa\b': 'health insurance portability accountability act',
        r'\bpci\b': 'payment card industry',
        r'\bsox\b': 'sarbanes oxley',
        r'\biso\b': 'international organization for standardization',
        r'\bip\b': 'intellectual property',
        r'\bpii\b': 'personally identifiable information',
        r'\bnda\b': 'non disclosure agreement',
        r'\bsla\b': 'service level agreement',
        r'\bsso\b': 'single sign on',
        r'\bmfa\b': 'multi factor authentication',
    }
    
    for abbrev, expansion in abbreviations.items():
        text = re.sub(abbrev, expansion, text)
    
    return text


def remove_artifacts(text: str) -> str:
    """
    Remove OCR artifacts, noise, and document generation artifacts.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove common OCR artifacts (repeated characters)
    text = re.sub(r'([^\w\s])\1{3,}', r'\1', text)
    
    # Remove isolated special characters
    text = re.sub(r'[\s][^\w\s@.-]{1,3}[\s]', ' ', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!?]{3,}', '!', text)
    text = re.sub(r'\.{3,}', '.', text)
    
    # Remove common noise patterns
    text = re.sub(r'[\s]*\|[\s]*', ' ', text)
    text = re.sub(r'[\s]*\\[\s]*', ' ', text)
    
    return text.strip()


def enhance_compliance_normalization(text: str) -> str:
    """
    Apply all normalization techniques for optimal compliance evaluation.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Fully normalized text
    """
    if not text:
        return ""
    
    # Apply normalization in sequence
    text = remove_artifacts(text)
    text = normalize_whitespace(text)
    text = normalize_special_characters(text)
    text = normalize_abbreviations(text)
    text = normalize_text_for_compliance(text)
    
    return text


def extract_sensitive_data(text: str) -> dict:
    """
    Extract and categorize sensitive data found in text.
    
    Args:
        text: Document text to scan
        
    Returns:
        Dictionary with categorized sensitive findings
    """
    normalized = text.lower()
    
    findings = {
        "ssn": re.findall(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', normalized),
        "credit_card": re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', normalized),
        "email": re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', normalized),
        "phone": re.findall(r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b', normalized),
    }
    
    return findings


def detect_document_version(text: str, file_name: str = "") -> str:
    """Attempt to detect a document version from text or filename.

    Returns a normalized version string like 'v1.0' if found, else empty string.
    """
    if not text and not file_name:
        return ""

    normalized = (text or "").lower()

    # Common patterns: 'version: v1.0', 'version 1.0', 'rev. 1.0', 'v1.0'
    patterns = [
        r'version\s*[:\-]?\s*v?(\d+(?:\.\d+)+)',
        r'rev(?:ision)?\s*[:\-]?\s*v?(\d+(?:\.\d+)+)',
        r'\bv(\d+(?:\.\d+)+)\b',
        r'\b(\d+\.\d+(?:\.\d+)*)\b',
    ]

    for pat in patterns:
        m = re.search(pat, normalized, flags=re.IGNORECASE)
        if m:
            ver = m.group(1)
            return f'v{ver}' if not ver.startswith('v') else ver

    # Fallback: try to parse version from filename (e.g., mydoc_v1.2.docx)
    if file_name:
        m = re.search(r'v(\d+(?:\.\d+)+)', file_name.lower())
        if m:
            return f'v{m.group(1)}'

    return ""


RULES = [
    {
        "id": "GDP-01",
        "title": "Document title on first page matches file name",
        "severity": "High",
        "violation": "",
        "evidence": "Disaster Re..."
    },
    {
        "id": "GDP-02",
        "title": "Author name and role are mentioned",
        "severity": "High",
        "violation": "",
        "evidence": "Owner"
    },
    {
        "id": "GDP-03",
        "title": "Dates in revision history are valid",
        "severity": "High",
        "violation": "",
        "evidence": "No issues detected."
    },
    {
        "id": "GDP-04",
        "title": "Version number presence",
        "severity": "High",
        "violation": "",
        "evidence": "Text: Version..."
    },
    {
        "id": "GDP-05",
        "title": "Revision section is present",
        "severity": "High",
        "violation": "",
        "evidence": "Revision History"
    },
    {
        "id": "GDP-06",
        "title": "Signature blocks are present",
        "severity": "High",
        "violation": "",
        "evidence": "First Page:..."
    },
    {
        "id": "GDP-07",
        "title": "Dates present near signatures",
        "severity": "Medium",
        "violation": "",
        "evidence": "First Page:..."
    },
    {
        "id": "GDP-08",
        "title": "Basic font and spacing consistency",
        "severity": "Low",
        "violation": "",
        "evidence": "2 font(s) used"
    },
    {
        "id": "GDP-09",
        "title": "Language errors identified",
        "severity": "Medium",
        "violation": "",
        "evidence": "No issues detected."
    },
    {
        "id": "GDP-10",
        "title": "Required sections present (Objective, Scope, etc.)",
        "severity": "High",
        "violation": "",
        "evidence": "Required sections present"
    },
    {
        "id": "GDP-11",
        "title": "Page numbers present and sequential",
        "severity": "Medium",
        "violation": "",
        "evidence": "Single page..."
    },
    {
        "id": "GDP-12",
        "title": "Readability within acceptable range",
        "severity": "Low",
        "violation": "",
        "evidence": "Score=39..."
    },
    {
        "id": "GDP-13",
        "title": "Footer completeness",
        "severity": "Medium",
        "violation": "",
        "evidence": "Footer appears to be complete."
    }
    ,
    {
        "id": "GDP-14",
        "title": "Compliance statement presence",
        "severity": "High",
        "violation": "",
        "evidence": "Compliance statement section presence will be checked."
    }
]

COMPLIANCE_ITEMS = [
    {
        "title": "Data Privacy",
        "description": "Do not upload sensitive personal or confidential data unless permitted.",
        "level": "High"
    },
    {
        "title": "Document Ownership",
        "description": "Ensure you have rights to process and analyze uploaded documents.",
        "level": "Medium"
    },
    {
        "title": "Retention",
        "description": "Temporary files are deleted after processing but keep your workspace secure.",
        "level": "Medium"
    },
    {
        "title": "Accuracy Review",
        "description": "Review extracted text before making decisions or sharing results.",
        "level": "Low"
    },
    {
        "title": "Regulatory Compliance",
        "description": "Use this tool in accordance with applicable policies and standards.",
        "level": "High"
    }
]

COMPLIANCE_RULES = [
    {
        "id": "CMP-01",
        "title": "Data Privacy",
        "severity": "High",
        "pattern": r"(\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b|\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|[\w.+-]+@[\w-]+\.[\w.-]+|\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b)",
        "fail_message": "Potential sensitive personal data detected.",
        "pass_message": "No sensitive personal data patterns detected."
    },
    {
        "id": "CMP-02",
        "title": "Document Ownership",
        "severity": "Medium",
        "pattern": r"(copyright|©|®|™|all rights reserved|proprietary|trademark|confidential|classified|restricted|ownership|intellectual property|patent|licensed|license|reserved|company proprietary|internal use only)",
        "pass_message": "Document ownership and rights language detected."
    },
    {
        "id": "CMP-03",
        "title": "Accuracy Review",
        "severity": "Low",
        "pattern": r"(\?\?|\bunknown\b|\bnot available\b|\bsee above\b)",
        "fail_message": "Extraction may contain questionable or incomplete content.",
        "pass_message": "No questionable or incomplete content detected."
    },
    {
        "id": "CMP-04",
        "title": "Regulatory Compliance",
        "severity": "High",
        "pattern": r"(compliance|gdpr|hipaa|pci|sox|iso 27001|security policy|privacy policy)",
        "pass_message": "Regulatory compliance language detected."
    }
]

VALIDATION_RULES = [
    {
        "id": "VAL-001",
        "title": "Title Cannot Be Blank",
        "category": "business",
        "severity": "critical",
        "rule_type": "deterministic",
        "phase": "phase_1",
        "verifiable_criteria": "Verify that the document title exists and is not empty.",
        "recommendation": "Add a valid document title."
    },
    {
        "id": "VAL-002",
        "title": "Version Format Validation",
        "category": "business",
        "severity": "high",
        "rule_type": "deterministic",
        "phase": "phase_1",
        "verifiable_criteria": "Verify that version follows format vX.X.",
        "recommendation": "Update version to approved format."
    }
    # {
    #     "id": "VAL-003",
    #     "title": "Revision History Validation",
    #     "category": "business",
    #     "severity": "high",
    #     "rule_type": "deterministic",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "Verify revision history contains date, change summary, and initiator.",
    #     "recommendation": "Complete revision history information."
    # },
    # {
    #     "id": "VAL-004",
    #     "title": "AI Confidence Threshold Validation",
    #     "category": "system",
    #     "severity": "medium",
    #     "rule_type": "system",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "If AI confidence score is below 0.5, route document for manual review.",
    #     "recommendation": "Perform manual review."
    # },
    # {
    #     "id": "VAL-005",
    #     "title": "Approval Matrix Validation",
    #     "category": "business",
    #     "severity": "critical",
    #     "rule_type": "hybrid",
    #     "phase": "phase_2",
    #     "verifiable_criteria": "Verify signatures match the required role-based approval matrix.",
    #     "recommendation": "Add missing approvers or signatures."
    # },
    # {
    #     "id": "VAL-006",
    #     "title": "Traceability Validation",
    #     "category": "business",
    #     "severity": "critical",
    #     "rule_type": "semantic",
    #     "phase": "phase_2",
    #     "verifiable_criteria": "Verify traceability mapping exists between URS, FRS, and Test Cases.",
    #     "recommendation": "Complete traceability matrix."
    # },
    # {
    #     "id": "VAL-007",
    #     "title": "Unauthorized Edit Detection",
    #     "category": "system",
    #     "severity": "critical",
    #     "rule_type": "system",
    #     "phase": "phase_2",
    #     "verifiable_criteria": "Verify document changes are authorized and tracked through change control process.",
    #     "recommendation": "Review audit logs and version history."
    # },
    # {
    #     "id": "VAL-008",
    #     "title": "Audit Trail Validation",
    #     "category": "regulatory",
    #     "severity": "critical",
    #     "rule_type": "system",
    #     "phase": "phase_2",
    #     "verifiable_criteria": "Verify audit logs are tamper-proof and contain complete change history.",
    #     "recommendation": "Enable compliant audit trail mechanism."
    # },
    # {
    #     "id": "VAL-009",
    #     "title": "Electronic Signature Compliance",
    #     "category": "regulatory",
    #     "severity": "critical",
    #     "rule_type": "hybrid",
    #     "phase": "phase_2",
    #     "verifiable_criteria": "Verify electronic signatures comply with CFR 21 Part 11 requirements.",
    #     "recommendation": "Use compliant electronic signature solution."
    # },
    # {
    #     "id": "VAL-010",
    #     "title": "Supported File Type Validation",
    #     "category": "system",
    #     "severity": "high",
    #     "rule_type": "deterministic",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "Verify that the uploaded file is PDF, DOCX, or TXT.",
    #     "recommendation": "Upload a supported document format."
    # },
    # {
    #     "id": "VAL-011",
    #     "title": "Readable Document Validation",
    #     "category": "system",
    #     "severity": "high",
    #     "rule_type": "deterministic",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "Verify that the uploaded document can be opened and read.",
    #     "recommendation": "Check file integrity and remove password protection or corruption."
    # },
    # {
    #     "id": "VAL-012",
    #     "title": "Text Extraction Validation",
    #     "category": "system",
    #     "severity": "high",
    #     "rule_type": "system",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "Verify that text extraction returned readable content.",
    #     "recommendation": "Ensure the document contains text that can be extracted."
    # },
    # {
    #     "id": "VAL-013",
    #     "title": "Rules File Extraction Validation",
    #     "category": "system",
    #     "severity": "medium",
    #     "rule_type": "semantic",
    #     "phase": "phase_1",
    #     "verifiable_criteria": "Verify that an uploaded rules file contains readable rule text.",
    #     "recommendation": "Upload a readable rules file or convert it to a supported text format."
    # }
]


def evaluate_validation_rules(document_text: str, document_title: str = "", version: str = "", metadata: dict = None, ai_confidence_score: float = None, file_name: str = ""):
    """Evaluate document validation rules with deterministic checks."""
    text = document_text or ""
    normalized_text = enhance_compliance_normalization(text)
    metadata = metadata or {}

    # Determine extracted title: prefer explicit document_title, else first non-empty line
    extracted_title = (document_title or "").strip()
    if not extracted_title:
        for line in document_text.splitlines():
            if line.strip():
                extracted_title = line.strip()
                break

    # Default AI confidence heuristic
    if ai_confidence_score is None:
        ai_confidence_score = 0.75 if len(normalized_text) > 250 else 0.45

    results = []

    # helper checks
    version_pattern = re.compile(r'\bv\d+\.\d+\b', flags=re.IGNORECASE)
    # attempt to detect version automatically if not supplied
    detected_version = ""
    if not version:
        detected_version = detect_document_version(document_text, file_name or metadata.get('file_name', ''))
        if detected_version:
            version = detected_version
    date_patterns = [re.compile(r'\b\d{4}-\d{2}-\d{2}\b'), re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', flags=re.IGNORECASE)]
    signature_pattern = re.compile(r'(signature|signed by|approved by)', flags=re.IGNORECASE)
    traceability_pattern = re.compile(r'(traceability|traceability matrix|urs|frs|test case|test cases)', flags=re.IGNORECASE)
    audit_pattern = re.compile(r'(audit trail|audit log|audit)', flags=re.IGNORECASE)

    for rule in VALIDATION_RULES:
        rid = rule["id"]
        # Start as NOT_EVALUATED to avoid defaulting to PASS when no check exists.
        status = "NOT_EVALUATED"
        evidence = "No automated check implemented for this rule."

        # VAL-001: Title Cannot Be Blank
        if rid == "VAL-001":
            if not extracted_title:
                status = "FAIL"
                evidence = "Document title is blank or missing. Provide a non-empty title on the first page."
            else:
                status = "PASS"
                evidence = f"Title found on first non-empty line: '{extracted_title}'."

        # VAL-002: Version Format Validation
        elif rid == "VAL-002":
            # Prefer explicit version (detected or provided), else search text
            version_source = (version or '').strip() or normalized_text
            m = version_pattern.search(version_source)
            if not m:
                status = "FAIL"
                evidence = "Version not found in expected format 'vX.X'. Example acceptable format: 'v1.0'."
                if detected_version:
                    evidence = f"Attempted auto-detection found '{detected_version}' but not in expected 'vX.X' form in context."
            else:
                status = "PASS"
                evidence = f"Version format detected: '{m.group(0)}'."

        # VAL-003: Revision History Validation
        elif rid == "VAL-003":
            has_revision = 'revision' in normalized_text or 'revision history' in normalized_text
            date_match = None
            for p in date_patterns:
                m = p.search(normalized_text)
                if m:
                    date_match = m.group(0)
                    break
            if not (has_revision and date_match):
                status = "FAIL"
                evidence = "Revision history or associated dates missing; include a revision section with dates (e.g. 2023-05-01)."
            else:
                status = "PASS"
                evidence = f"Revision history and date detected; example date: {date_match}."

        # VAL-004: AI Confidence Threshold Validation
        elif rid == "VAL-004":
            if ai_confidence_score < 0.5:
                status = "FAIL"
                evidence = f"AI confidence score {ai_confidence_score:.2f} below threshold 0.5 — recommend manual review."
            else:
                status = "PASS"
                evidence = f"AI confidence score {ai_confidence_score:.2f} meets automated validation threshold."

        # VAL-005: Approval Matrix Validation
        elif rid == "VAL-005":
            sig = signature_pattern.search(normalized_text)
            if not sig:
                status = "FAIL"
                evidence = "No signature or approval phrases detected (e.g. 'Signature:', 'Signed by', 'Approved by')."
            else:
                status = "PASS"
                evidence = f"Approval indicator detected: '{sig.group(0)}'. Verify signatures match the approval matrix."

        # VAL-006: Traceability Validation
        elif rid == "VAL-006":
            tr = traceability_pattern.search(normalized_text)
            if not tr:
                status = "FAIL"
                evidence = "Traceability keywords (URS/FRS/Test Cases/traceability) not found. Include traceability mapping."
            else:
                status = "PASS"
                evidence = f"Traceability language detected: '{tr.group(0)}'."

        # VAL-007: Unauthorized Edit Detection
        elif rid == "VAL-007":
            # If metadata explicitly flags unauthorized edits, fail; else pass
            if metadata.get('unauthorized_edits') is True:
                status = "FAIL"
                evidence = "Metadata flag 'unauthorized_edits' is true — changes may be unauthorized; review audit logs."
            else:
                status = "PASS"
                evidence = "No metadata indicator of unauthorized edits; no automated evidence found."

        # VAL-008: Audit Trail Validation
        elif rid == "VAL-008":
            aud = audit_pattern.search(normalized_text)
            if not aud and not metadata.get('has_audit_trail'):
                status = "FAIL"
                evidence = "No audit trail references detected and metadata does not indicate audit capability."
            else:
                status = "PASS"
                evidence = "Audit trail references or metadata indicate audit capability."

        # VAL-009: Electronic Signature Compliance
        elif rid == "VAL-009":
            esc_found = None
            for term in ('electronic signature', '21 cfr part 11', 'cfr 21 part 11', 'part 11'):
                if term in normalized_text:
                    esc_found = term
                    break
            if esc_found:
                status = "PASS"
                evidence = f"Electronic signature compliance language detected: '{esc_found}'. Verify with CFR 21 Part 11 requirements."
            else:
                status = "FAIL"
                evidence = "Electronic signature compliance language not detected (CFR 21 Part 11)."

        # VAL-010: Supported File Type Validation
        elif rid == "VAL-010":
            fname = (file_name or metadata.get('file_name', '')).lower()
            if not any(fname.endswith(ext) for ext in ('.pdf', '.docx', '.txt')):
                status = "FAIL"
                evidence = f"Unsupported file type: '{fname or 'unknown'}'. Expected PDF, DOCX, or TXT."
            else:
                status = "PASS"
                evidence = f"Supported file type detected: '{fname}'."

        # VAL-011: Readable Document Validation
        elif rid == "VAL-011":
            words = re.findall(r'\w+', normalized_text)
            if len(words) < 20:
                status = "FAIL"
                evidence = f"Document appears unreadable or too short ({len(words)} words)."
            else:
                status = "PASS"
                evidence = f"Document readability OK ({len(words)} words)."

        # VAL-012: Text Extraction Validation
        elif rid == "VAL-012":
            words = re.findall(r'\w+', normalized_text)
            if len(words) < 5:
                status = "FAIL"
                evidence = f"Text extraction returned insufficient content ({len(words)} words)."
            else:
                status = "PASS"
                evidence = "Text extraction returned readable content."

        # VAL-013: Rules File Extraction Validation
        elif rid == "VAL-013":
            if 'rule' not in normalized_text and 'validation' not in normalized_text:
                status = "FAIL"
                evidence = "Uploaded rules file does not contain readable rule text (no 'rule' or 'validation' keywords found)."
            else:
                # provide a short snippet where 'rule' appears
                m = re.search(r'.{0,30}rule.{0,30}', normalized_text)
                snippet = m.group(0) if m else 'rules keywords present'
                status = "PASS"
                evidence = f"Rules content detected: {snippet}"

        # default fallback for unimplemented rules
        else:
            status = "NOT_EVALUATED"
            evidence = "No deterministic check implemented for this validation rule."

        results.append({
            "id": rid,
            "title": rule["title"],
            "category": rule["category"],
            "severity": rule["severity"],
            "rule_type": rule["rule_type"],
            "phase": rule["phase"],
            "verifiable_criteria": rule["verifiable_criteria"],
            "recommendation": rule["recommendation"],
            "status": status,
            "evidence": evidence,
            "confidence_score": round(ai_confidence_score, 2),
        })

    return results


def evaluate_compliance(document_text: str, validation_results: list = None):
    """Evaluate compliance rules using regex patterns from COMPLIANCE_RULES."""
    text = document_text or ""
    normalized_text = enhance_compliance_normalization(text)

    results = []
    for rule in COMPLIANCE_RULES:
        pat = rule.get('pattern')
        try:
            regex = re.compile(pat, flags=re.IGNORECASE)
        except Exception:
            regex = None

        matches = regex.findall(normalized_text) if regex else []

        # Determine status semantics per rule id
        if rule['id'] == 'CMP-01':
            # sensitive data -> FAIL if matches found
            status = 'FAIL' if matches else 'PASS'
            evidence = rule.get('fail_message') if matches else rule.get('pass_message')
        elif rule['id'] == 'CMP-03':
            # questionable extraction tokens -> FAIL if matches
            status = 'FAIL' if matches else 'PASS'
            evidence = rule.get('fail_message') if matches else rule.get('pass_message')
        else:
            # for ownership and regulatory, presence is desirable -> PASS if matches
            status = 'PASS' if matches else 'FAIL'
            evidence = rule.get('pass_message') if matches else f"No {rule['title']} language detected."

        results.append({
            'id': rule['id'],
            'title': rule['title'],
            'status': status,
            'severity': rule.get('severity'),
            'evidence': evidence,
            'matches': matches
        })

    # If validation results are provided and validation did not fully PASS,
    # mark compliance evaluation as BLOCKED to prevent ambiguous guidance.
    try:
        if validation_results:
            summary = summarize_rule_results(validation_results)
            overall = summary.get('overall_status')
            if overall != 'PASS':
                note = f' (Compliance evaluation BLOCKED due to validation status: {overall}.)'
                for r in results:
                    r['status'] = 'BLOCKED'
                    r['evidence'] = (r.get('evidence', '') or '') + note
    except Exception:
        pass

    return results


def evaluate_document_rules(document_text: str, validation_results: list = None):
    """Evaluate document rules with simple heuristics.

    If `validation_results` is provided (list of VAL rule results), and all
    validation checks passed (no FAIL), then the GDP rules will be marked
    as PASS to reflect successful validation.
    """
    text = document_text or ""
    normalized = enhance_compliance_normalization(text)

    # Do NOT auto-compute validation results here. Only use provided
    # `validation_results` to decide whether to BLOCK GDP evaluations.

    # helpers
    date_re = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
    page_re = re.compile(r'page\s+(\d+)', flags=re.IGNORECASE)
    signature_re = re.compile(r'(signature|signed by|approved by)', flags=re.IGNORECASE)
    version_re = re.compile(r'\bv\d+\.\d+\b', flags=re.IGNORECASE)

    results = []
    # get first non-empty line as title
    extracted_title = ""
    for line in document_text.splitlines():
        if line.strip():
            extracted_title = line.strip()
            break

    for rule in RULES:
        rid = rule['id']
        # Start as NOT_EVALUATED to avoid accidentally defaulting to PASS
        status = 'NOT_EVALUATED'
        evidence = 'No automated check executed for this GDP rule.'

        if rid == 'GDP-01':
            if not extracted_title:
                status = 'FAIL'
                evidence = 'Document title missing on first page.'
            else:
                status = 'PASS'
                evidence = f'Title on first page: {extracted_title}'

        elif rid == 'GDP-02':
            if 'author' in normalized or 'owner' in normalized:
                status = 'PASS'
                evidence = 'Author name/role present.'
            else:
                status = 'FAIL'
                evidence = 'Author name or role not detected.'

        elif rid == 'GDP-03':
            if date_re.search(normalized):
                status = 'PASS'
                evidence = 'Revision dates detected.'
            else:
                status = 'FAIL'
                evidence = 'Revision dates not found.'

        elif rid == 'GDP-04':
            if version_re.search(normalized):
                status = 'PASS'
                evidence = 'Version number detected.'
            else:
                status = 'FAIL'
                evidence = 'Version number not detected.'

        elif rid == 'GDP-05':
            if 'revision' in normalized:
                status = 'PASS'
                evidence = 'Revision section present.'
            else:
                status = 'FAIL'
                evidence = 'Revision section not found.'

        elif rid == 'GDP-06':
            if signature_re.search(normalized):
                status = 'PASS'
                evidence = 'Signature blocks detected.'
            else:
                status = 'FAIL'
                evidence = 'Signature blocks not detected.'

        elif rid == 'GDP-07':
            if signature_re.search(normalized) and date_re.search(normalized):
                status = 'PASS'
                evidence = 'Dates present near signatures.'
            else:
                status = 'FAIL'
                evidence = 'Dates near signatures not detected.'

        elif rid == 'GDP-08':
            status = 'PASS'
            evidence = rule.get('evidence', 'Formatting checked heuristically.')

        elif rid == 'GDP-09':
            # enhanced language error detection
            issues = []
            # common misspellings and placeholders
            misspellings = ('teh', 'recieve', 'seperate', 'occured', 'adress')
            placeholders = ('lorem ipsum', 'xxx', 'yyy')
            for token in misspellings + placeholders:
                if token in normalized:
                    issues.append(token)

            # punctuation and spacing issues
            if '  ' in document_text:
                issues.append('double-space')
            if document_text.count('(') != document_text.count(')'):
                issues.append('unbalanced-parentheses')
            if '??' in document_text or '???' in document_text:
                issues.append('question-marks')

            # short heuristics for repeated characters like 'aaaa' or '----'
            if re.search(r'(\w)\1{3,}', normalized):
                issues.append('repeated-characters')

            if issues:
                status = 'FAIL'
                evidence = 'Language issues detected: ' + ','.join(sorted(set(issues)))
            else:
                status = 'PASS'
                evidence = 'No obvious language errors detected.'

        elif rid == 'GDP-10':
            required = ('objective', 'scope', 'introduction')
            found = [s for s in required if s in normalized]
            if len(found) >= 2:
                status = 'PASS'
                evidence = 'Required sections present.'
            else:
                status = 'FAIL'
                evidence = f'Missing required sections; found: {found}'

        elif rid == 'GDP-11':
            pages = [int(m) for m in page_re.findall(document_text)]
            if pages and pages == list(range(min(pages), max(pages) + 1)):
                status = 'PASS'
                evidence = 'Page numbers present and sequential.'
            elif pages:
                status = 'FAIL'
                evidence = f'Page numbers found but not sequential: {pages}'
            else:
                status = 'FAIL'
                evidence = 'Page numbers not detected.'

        elif rid == 'GDP-12':
            words = re.findall(r'\w+', normalized)
            if len(words) >= 100:
                status = 'PASS'
                evidence = 'Readability within acceptable range.'
            else:
                status = 'FAIL'
                evidence = f'Readability low ({len(words)} words).'

        elif rid == 'GDP-13':
            if 'footer' in normalized or '©' in document_text or 'page' in normalized:
                status = 'PASS'
                evidence = 'Footer appears to be present.'
            else:
                status = 'FAIL'
                evidence = 'Footer completeness not detected.'

        elif rid == 'GDP-14':
            # Check for common compliance/regulatory declaration language
            compliance_terms = ('compliance statement', 'regulatory', 'gxp', 'iso', 'regulatory declarations', 'compliance', 'regulatory statement')
            found = any(term in normalized for term in compliance_terms)
            if found:
                status = 'PASS'
                evidence = 'Compliance/regulatory statement language detected.'
            else:
                status = 'FAIL'
                evidence = 'Compliance statement section not detected; include applicable regulatory declarations (e.g., GxP, ISO).'

        results.append({
            'id': rid,
            'title': rule['title'],
            'status': status,
            'severity': rule['severity'],
            'violation': rule.get('violation', ''),
            'evidence': evidence,
        })

    # If validation results are provided, append a validation summary note to GDP evidence
    # ONLY append when validation overall is PASS. If any VAL rule is WARNING/FAIL,
    # do not mix validation summary into GDP evidence to avoid conflicting/ambiguous results.
    try:
        if validation_results:
            summary = summarize_rule_results(validation_results)
            overall = summary.get('overall_status')
            if overall == 'PASS':
                note = ' (Validated by VAL rules: all checks passed.)'
                for r in results:
                    r['evidence'] = (r.get('evidence', '') or '') + note
            else:
                # When validation produced WARNING or FAIL, BLOCK GDP rules to avoid mixing
                # potentially unreliable GDP PASS/FAIL with validation issues.
                note = f' (GDP evaluation BLOCKED due to validation status: {overall}.)'
                for r in results:
                    r['status'] = 'BLOCKED'
                    r['evidence'] = (r.get('evidence', '') or '') + note
    except Exception:
        # best-effort: if summarization fails, leave results as-is
        pass

    return results


def summarize_rule_results(rule_results: list) -> dict:
    """
    Summarize rule results into counts and an overall status.

    Returns:
        dict with keys: pass_count, warning_count, fail_count, overall_status
    """
    pass_count = sum(1 for r in rule_results if r.get("status") == "PASS")
    warning_count = sum(1 for r in rule_results if r.get("status") == "WARNING")
    fail_count = sum(1 for r in rule_results if r.get("status") == "FAIL")

    if fail_count > 0:
        overall = "FAIL"
    elif warning_count > 0:
        overall = "WARNING"
    else:
        overall = "PASS"

    return {
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "overall_status": overall,
    }


if __name__ == "__main__":
    # Quick print for debugging
    for r in RULES:
        print(f"{r['id']}: {r['title']} - {r['status']} ({r['severity']})")
