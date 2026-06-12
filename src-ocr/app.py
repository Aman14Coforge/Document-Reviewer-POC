"""
Document Extractor Chatbot - Main Streamlit Application
This application uses OCR to extract text from documents and provides a chatbot interface
"""

import streamlit as st
import os
from pathlib import Path
from ocr_processor import OCRProcessor
from chatbot import DocumentChatbot
from config import OPENAI_API_KEY
from rules import evaluate_compliance, evaluate_document_rules, evaluate_validation_rules, summarize_rule_results
from ui_components import display_header, display_chat_interface, display_statistics

# Set page configuration
st.set_page_config(
    page_title="Document Extractor Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    body, .stApp, .block-container {
        background: linear-gradient(180deg, #eaf1ff 0%, #f8fbff 100%) !important;
    }
    .block-container {
        padding-top: 24px !important;
        padding-bottom: 24px !important;
        border-radius: 28px;
        box-shadow: 0 30px 80px rgba(15, 56, 125, 0.08);
    }
    .main {
        padding: 0rem 0rem;
    }
    .app-card {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(43, 110, 246, 0.12);
        border-radius: 24px;
        padding: 24px 28px;
        box-shadow: 0 24px 60px rgba(45, 78, 128, 0.08);
        transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    }
    .app-card:hover {
        transform: translateY(-3px);
        border-color: rgba(43, 110, 246, 0.22);
        box-shadow: 0 30px 80px rgba(45, 78, 128, 0.14);
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(43, 110, 246, 0.12), rgba(255, 255, 255, 0.9));
        border: 1px solid rgba(43, 110, 246, 0.16);
        border-radius: 26px;
    }
    .metric-card {
        background: linear-gradient(180deg, #ffffff, #f6f9ff);
        border: 1px solid rgba(43, 110, 246, 0.1);
        border-radius: 22px;
        padding: 22px;
        transition: transform 0.18s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .stSidebar {
        background: linear-gradient(180deg, #ffffff, #eef5ff) !important;
        border-right: 1px solid rgba(43, 110, 246, 0.12);
        box-shadow: inset -1px 0 0 rgba(43, 110, 246, 0.06);
    }
    .stButton>button {
        width: 100% !important;
        min-height: 50px;
        border-radius: 14px;
        background: linear-gradient(135deg, #2b6ef6, #5eb2ff) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 14px 30px rgba(43, 110, 246, 0.18);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2559e0, #53a6ff) !important;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div>div {
        border-radius: 14px !important;
        border: 1px solid rgba(43, 110, 246, 0.16) !important;
        box-shadow: inset 0 1px 2px rgba(15, 56, 125, 0.05);
    }
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 18px !important;
        background: rgba(255,255,255,0.94) !important;
        color: #1d3b78 !important;
        border: 1px solid rgba(43,110,246,0.14) !important;
        padding: 16px 22px !important;
        min-width: 180px;
        margin: 4px !important;
        box-shadow: 0 12px 24px rgba(15, 55, 125, 0.08);
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        background: linear-gradient(135deg, #f4f8ff, #f0f5ff) !important;
    }
    .stTabs [data-baseweb="tab-list"] button[data-selected="true"] {
        background: linear-gradient(135deg, #2b6ef6, #5eb2ff) !important;
        color: #ffffff !important;
        border-color: rgba(43, 110, 246, 0.32) !important;
        box-shadow: 0 18px 36px rgba(43, 110, 246, 0.18);
    }
    .stTabs [data-baseweb="tab-list"] button[data-selected="true"] [data-testid="stMarkdownContainer"] p {
        font-weight: 700 !important;
    }
    .stProgress > div > div > div {
        border-radius: 999px;
    }
    @media (max-width: 768px) {
        .css-1lcbmhc.e1tzin5v1 {
            padding: 0 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    # Initialize default session state values
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if "compliance_results" not in st.session_state:
        st.session_state.compliance_results = []
    if "rule_results" not in st.session_state:
        st.session_state.rule_results = []
    if "summary_text" not in st.session_state:
        st.session_state.summary_text = ""
    if "metadata" not in st.session_state:
        st.session_state.metadata = {}
    if "document_title" not in st.session_state:
        st.session_state.document_title = ""
    if "validation_status" not in st.session_state:
        st.session_state.validation_status = ""
    if "validation_passed" not in st.session_state:
        st.session_state.validation_passed = False
    if "validation_results" not in st.session_state:
        st.session_state.validation_results = []
    if "validation_confidence_score" not in st.session_state:
        st.session_state.validation_confidence_score = 0.0
    if "validation_completed" not in st.session_state:
        st.session_state.validation_completed = False
    if "validation_summary" not in st.session_state:
        st.session_state.validation_summary = {"pass_count": 0, "warning_count": 0, "fail_count": 0, "overall_status": ""}
    if "review_completed" not in st.session_state:
        st.session_state.review_completed = False
    if "validation_in_progress" not in st.session_state:
        st.session_state.validation_in_progress = False
    if "review_in_progress" not in st.session_state:
        st.session_state.review_in_progress = False


def display_sidebar_metadata():
    """Display metadata and compliance summary in the sidebar."""
    st.sidebar.markdown("## 📄 Document Info")
    
    if st.session_state.metadata:
        meta = st.session_state.metadata
        
        # File info section
        with st.sidebar.expander("📋 File Details", expanded=True):
            if "file_name" in meta:
                st.markdown(f"**File:** {meta['file_name']}")
            if "file_size_bytes" in meta:
                size_kb = meta["file_size_bytes"] / 1024
                st.markdown(f"**Size:** {size_kb:.1f} KB")
            if "extension" in meta:
                st.markdown(f"**Type:** {meta['extension'].upper()}")
            
            # Timestamps
            if "created_time" in meta or "modified_time" in meta:
                st.markdown("---")
                if "created_time" in meta:
                    created = meta["created_time"].split("T")[0]
                    st.markdown(f"📅 Created: {created}")
                if "modified_time" in meta:
                    modified = meta["modified_time"].split("T")[0]
                    st.markdown(f"✏️ Modified: {modified}")
        
        # Document properties
        if "document" in meta and meta["document"]:
            doc_meta = meta["document"]
            if "error" not in doc_meta:
                with st.sidebar.expander("🔍 Properties", expanded=False):
                    for key, value in doc_meta.items():
                        if key not in ["info", "exif"]:
                            display_val = str(value)[:40]
                            st.markdown(f"- **{key}**: {display_val}")
        
        st.sidebar.divider()
    else:
        st.sidebar.info("📋 Upload a document to view metadata.")

        # Validation status: show results when completed, subtle placeholder when in progress
        if st.session_state.validation_completed:
            if st.session_state.validation_status:
                with st.sidebar.expander("🛡️ Validation Status", expanded=False):
                    if st.session_state.validation_passed:
                        st.success(st.session_state.validation_status)
                    else:
                        st.error(st.session_state.validation_status)
        elif st.session_state.validation_in_progress:
            with st.sidebar.expander("🛡️ Validation Status", expanded=False):
                st.info("Validation in progress — results will appear here when complete.")
    
    # Sidebar no longer displays compliance or rule summaries to avoid duplication

    # Note: validation summary is intentionally shown only in the Validation Dashboard


def get_supported_file_types():
    return ["pdf", "docx", "txt", "jpg", "jpeg", "png"]


def save_uploaded_file(uploaded_file):
    temp_path = Path("temp_upload")
    temp_path.mkdir(exist_ok=True)
    file_path = temp_path / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def cleanup_temp_upload(file_path):
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass


def extract_text_from_path(processor, file_path):
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return processor.extract_text_from_pdf(str(file_path))
    elif suffix == ".docx":
        return processor.extract_text_from_docx(str(file_path))
    elif suffix == ".txt":
        return processor.extract_text_from_txt(str(file_path))
    elif suffix in {".jpg", ".jpeg", ".png"}:
        return processor.extract_text_from_image(str(file_path))
    return ""


def report_extractability(extractable_ok, extract_msg, extract_details, continue_on_warning):
    if extractable_ok:
        return True

    if continue_on_warning:
        if "PDF" in extract_msg or "DOCX" in extract_msg or "Image" in extract_msg:
            st.warning(format_validation_message(extract_msg))
        else:
            st.warning(f"⚠️ {extract_msg}")
        st.info("Use the review button after validation to continue with the full GDP BOT review.")
    else:
        st.warning(f"⚠️ Extractability: {extract_msg}")
        st.info("Use the review button again to proceed with OCR despite warnings if needed.")

    with st.expander("Extraction diagnostics", expanded=False):
        st.json(extract_details)

    return continue_on_warning


def warn_if_empty_text(extracted_text, uploaded_file_name):
    if extracted_text.strip():
        return

    if "rule" in uploaded_file_name.lower():
        st.warning("⚠️ Could not extract rules from the uploaded rules file. Please verify it contains readable text.")
    else:
        st.warning("⚠️ Document appears to be empty or image-only. Text extraction returned no content.")


def get_dashboard_stage() -> str:
    if st.session_state.validation_results:
        return "Validation Complete"
    if st.session_state.rule_results or st.session_state.compliance_results:
        return "Review Complete"
    if st.session_state.uploaded_file_name:
        return "Ready for Review"
    return "Awaiting Upload"


def render_top_insights():
    extracted_text = st.session_state.extracted_text or ""
    char_count = len(extracted_text)
    stage = get_dashboard_stage()
    # Streamlit-native indicator when validation or review are running
    if st.session_state.get("validation_in_progress"):
        with st.container():
            st.info("⏳ Validation running — results will appear shortly...")
            st.progress(8)
    elif st.session_state.get("review_in_progress"):
        with st.container():
            st.info("🔄 Review running — generating insights...")
            st.progress(30)
    metrics = [
        ("Document", st.session_state.uploaded_file_name or "No document selected", "📄"),
        ("Stage", stage, "🚦"),
        ("Confidence", f"{int(st.session_state.validation_confidence_score * 100)}%", "🔍"),
        ("Extracted chars", f"{char_count}", "✍️"),
    ]

    col1, col2, col3, col4 = st.columns(4, gap="large")
    for idx, (label, value, emoji) in enumerate(metrics):
        with [col1, col2, col3, col4][idx]:
            st.markdown(
                f"<div class='app-card'>"
                f"<h4 style='margin:0; color:#0e3b90;'> {emoji} {label}</h4>"
                f"<p style='margin: 12px 0 0; font-size:1.1rem; color:#152238; font-weight:700;'>{value}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_wizard():
    st.markdown("<div class='app-card'> <h3>⏱️ Workflow Navigator</h3> <p>Follow the advanced review path below to complete document validation, compliance assessment, and AI-assisted analysis.</p></div>", unsafe_allow_html=True)
    step_cols = st.columns(4, gap="large")
    steps = [
        ("Upload File", "Select and configure your document details."),
        ("Validate", "Run file validation and extractability checks."),
        ("Review", "Perform compliance and document rule inspection."),
        ("Interact", "Ask questions and extract insights from your document."),
    ]
    for idx, (title, desc) in enumerate(steps):
        with step_cols[idx]:
            st.markdown(
                f"<div class='app-step'>"
                f"<strong style='font-size:1rem;'>Step {idx + 1}: {title}</strong>"
                f"<p style='margin: 10px 0 0; color:#475569;'>{desc}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_upload_tab():
    st.markdown("<div class='app-card'><h3>Upload & Configuration</h3><p>Set up your document payload with metadata, title, and validation context.</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        doc_type = st.selectbox("Document Type", ["SOP", "Policy", "Work Instruction", "Report"], index=0)
        version = st.text_input("Version", value="1.0")
        department = st.selectbox("Department", ["QA", "Engineering", "Operations", "HR", "Finance"], index=0)

        supported_types = get_supported_file_types()
        uploaded_file = st.file_uploader(
            "Drag & drop or select file",
            type=supported_types,
            help=f"Supported formats: {', '.join(ext.upper() for ext in supported_types)}",
            key="upload_input",
        )

        if uploaded_file is not None:
            default_title = Path(uploaded_file.name).stem.replace("_", " ").replace("-", " ").title()
            if not st.session_state.document_title:
                st.session_state.document_title = default_title
        document_title = st.text_input("Document Title", value=st.session_state.document_title)

        with st.expander("Advanced Upload Summary", expanded=False):
            st.markdown(f"- **Document Type:** {doc_type}")
            st.markdown(f"- **Version:** {version}")
            st.markdown(f"- **Department:** {department}")
            st.markdown(f"- **Title:** {document_title or 'Not set'}")

        if uploaded_file is None:
            st.info("Upload a PDF, DOCX, TXT, or image file to begin.")
        else:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > 50:
                st.error(f"❌ File is too large ({file_size_mb:.1f}MB). Maximum size is 50MB.")
            else:
                st.success(f"✅ File ready: {uploaded_file.name} ({file_size_mb:.1f}MB)")
                if st.button("Validate Document", key="validate_btn", use_container_width=True):
                    process_validation(uploaded_file, document_title, version, department)
                if st.button("Run GDP BOT Review", key="review_btn", use_container_width=True):
                    process_review(uploaded_file)

    with col2:
        st.markdown("<div class='app-card'><h4>Why this matters</h4><p>Use this advanced upload flow to capture metadata, validate content, and prepare the document for automated review.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='app-card'><h4>Quick Tips</h4><ul><li>Use descriptive document titles.</li><li>Choose the right department context.</li><li>Ensure the file is not password-protected.</li></ul></div>", unsafe_allow_html=True)

    return uploaded_file, document_title, version, department


def render_validation_tab():
    st.markdown("<div class='app-card'><h3>Validation Dashboard</h3><p>Interactive validation status, rule health, and extractability insight.</p></div>", unsafe_allow_html=True)
    if st.session_state.validation_completed:
        validation_pass = sum(1 for r in st.session_state.validation_results if r.get("status") == "PASS")
        validation_warn = sum(1 for r in st.session_state.validation_results if r.get("status") == "WARNING")
        validation_fail = sum(1 for r in st.session_state.validation_results if r.get("status") == "FAIL")
        validation_not_eval = sum(1 for r in st.session_state.validation_results if r.get("status") == "NOT_EVALUATED")

        # show extra column when there are NOT_EVALUATED rules to make counts explicit
        if validation_not_eval:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Validation Passed", validation_pass, delta="+0")
            with col2:
                st.metric("Validation Warnings", validation_warn, delta="+0")
            with col3:
                st.metric("Validation Failed", validation_fail, delta="+0")
            with col4:
                st.metric("Not Evaluated", validation_not_eval, delta="+0")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Validation Passed", validation_pass, delta="+0")
            with col2:
                st.metric("Validation Warnings", validation_warn, delta="+0")
            with col3:
                st.metric("Validation Failed", validation_fail, delta="+0")

        if validation_fail > 0:
            st.error("❌ Critical validation issues detected. Scroll for details.")
        elif validation_warn > 0:
            st.warning("⚠️ Some validation warnings were identified.")
        else:
            st.success("✅ Validation rules passed successfully.")

        with st.expander("View validation findings", expanded=True):
            def _status_display(s):
                if s == 'PASS':
                    return '✅ PASS'
                if s == 'WARNING':
                    return '⚠️ WARNING'
                if s == 'FAIL':
                    return '❌ FAIL'
                if s == 'NOT_EVALUATED':
                    return '⏸️ NOT_EVALUATED'
                if s == 'BLOCKED':
                    return '⛔ BLOCKED'
                return s

            st.dataframe(
                [
                    {
                        "Status": f"{_status_display(r['status'])}",
                        "ID": r["id"],
                        "Title": r["title"],
                        "Severity": r["severity"],
                        "Evidence": r["evidence"],
                        "Recommendation": r["recommendation"],
                    }
                    for r in st.session_state.validation_results
                ],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Run validation to see the advanced validation dashboard.")


def render_review_tab():
    st.markdown("<div class='app-card'><h3>Review & Insights</h3><p>In-depth compliance, rule, and extraction intelligence for your document.</p></div>", unsafe_allow_html=True)
    if st.session_state.review_completed:
        review_cols = st.columns(2, gap="large")
        with review_cols[0]:
            st.subheader("Compliance Summary")
            if st.session_state.compliance_results:
                pass_count = sum(1 for r in st.session_state.compliance_results if r.get("status") == "PASS")
                warning_count = sum(1 for r in st.session_state.compliance_results if r.get("status") == "WARNING")
                fail_count = sum(1 for r in st.session_state.compliance_results if r.get("status") == "FAIL")
                st.metric("Passed", pass_count)
                st.metric("Warnings", warning_count)
                st.metric("Failed", fail_count)
                with st.expander("Compliance details", expanded=True):
                        for result in st.session_state.compliance_results:
                            s = result.get("status")
                            if s == 'PASS':
                                status_icon = '✅'
                            elif s == 'WARNING':
                                status_icon = '⚠️'
                            elif s == 'BLOCKED':
                                status_icon = '⛔'
                            elif s == 'NOT_EVALUATED':
                                status_icon = '⏸️'
                            else:
                                status_icon = '❌'

                            st.markdown(f"**{status_icon} {result['id']} {result['title']}**")
                            st.caption(result.get('evidence', 'No evidence available.'))
            else:
                st.info("Run GDP BOT review to populate compliance results.")

        with review_cols[1]:
            st.subheader("Rule Checks")
            if st.session_state.rule_results:
                rule_pass = sum(1 for r in st.session_state.rule_results if r.get("status") == "PASS")
                rule_warning = sum(1 for r in st.session_state.rule_results if r.get("status") == "WARNING")
                rule_fail = sum(1 for r in st.session_state.rule_results if r.get("status") == "FAIL")
                st.metric("Passed", rule_pass)
                st.metric("Warnings", rule_warning)
                st.metric("Failed", rule_fail)
                with st.expander("Document rule results", expanded=True):
                    st.dataframe(
                        [
                            {
                                "Status": (
                                    '✅ PASS' if r['status']=='PASS' else
                                    '⚠️ WARNING' if r['status']=='WARNING' else
                                    '⛔ BLOCKED' if r['status']=='BLOCKED' else
                                    '⏸️ NOT_EVALUATED' if r['status']=='NOT_EVALUATED' else
                                    '❌ FAIL'
                                ),
                                "ID": r["id"],
                                "Title": r["title"],
                                "Severity": r["severity"],
                                "Evidence": r["evidence"],
                            }
                            for r in st.session_state.rule_results
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("Run GDP BOT review to populate rule check results.")

        if st.session_state.extracted_text:
            with st.expander("View extracted document text", expanded=False):
                st.text_area("Extracted Content Preview", st.session_state.extracted_text[:12000], height=320)
            display_statistics(st.session_state.extracted_text)
    else:
        st.info("Run GDP BOT review to see document insights.")


def render_chat_tab():
    st.markdown("<div class='app-card'><h3>Chat & Document Intelligence</h3><p>Ask questions, generate summaries, and extract key concepts from your document.</p></div>", unsafe_allow_html=True)
    if st.session_state.chatbot is not None:
        display_chat_interface()
    else:
        st.info("Run the GDP BOT review to activate the chat interface.")


def format_validation_message(raw_message: str) -> str:
    raw = raw_message.lower()
    if "unsupported file format" in raw:
        return "⚠️ Unsupported file type. Please upload PDF, DOCX, or TXT files only."
    if "encrypted" in raw or "password" in raw or "corrupt" in raw or "could not read" in raw:
        return "⚠️ Could not read file. Please check it is not password-protected or corrupt."
    return raw_message


def process_validation(uploaded_file, document_title, version, department):
    file_path = save_uploaded_file(uploaded_file)
    processor = OCRProcessor()
    try:
        st.session_state.validation_completed = False
        st.session_state.validation_in_progress = True
        is_valid, validation_message = processor.validate_file(str(file_path))
        st.session_state.validation_status = validation_message if not is_valid else "File validated successfully."
        st.session_state.validation_passed = is_valid

        if not is_valid:
            st.warning(format_validation_message(validation_message))
            return

        extractable_ok, extract_msg, extract_details = processor.validate_extractable(str(file_path))
        st.session_state.validation_status = extract_msg if not extractable_ok else st.session_state.validation_status
        report_extractability(extractable_ok, extract_msg, extract_details, continue_on_warning=True)

        progress_bar = st.progress(0)
        st.session_state.uploaded_file_name = uploaded_file.name

        progress_bar.progress(20)
        extracted_text = extract_text_from_path(processor, file_path)
        warn_if_empty_text(extracted_text, uploaded_file.name)

        st.session_state.extracted_text = extracted_text
        st.session_state.metadata = processor.extract_metadata(str(file_path))
        ai_confidence_score = 0.75 if len(extracted_text) > 250 else 0.45
        st.session_state.validation_confidence_score = ai_confidence_score
        st.session_state.validation_results = evaluate_validation_rules(
            extracted_text,
            document_title,
            version,
            st.session_state.metadata,
            ai_confidence_score,
            uploaded_file.name,
        )
        # store a canonical summary to avoid inconsistent counting in UI
        st.session_state.validation_summary = summarize_rule_results(st.session_state.validation_results)
        # Consider validation passed only if every validation rule explicitly PASSed.
        st.session_state.validation_passed = all(r.get("status") == "PASS" for r in st.session_state.validation_results)
        st.session_state.validation_completed = True
        progress_bar.progress(100)
        st.success("✅ Validation completed successfully.")
    except RuntimeError as e:
        st.error(f"❌ {e}")
    except Exception as e:
        st.error(f"❌ Error during validation: {str(e)}")
    finally:
        st.session_state.validation_in_progress = False
        cleanup_temp_upload(file_path)


def process_review(uploaded_file):
    file_path = save_uploaded_file(uploaded_file)
    processor = OCRProcessor()
    try:
        # reset review flag at start
        st.session_state.review_completed = False
        st.session_state.review_in_progress = True

        is_valid, validation_message = processor.validate_file(str(file_path))
        st.session_state.validation_status = validation_message if not is_valid else "File validated successfully."
        st.session_state.validation_passed = is_valid

        if not is_valid:
            st.error(f"❌ Validation failed: {validation_message}")
            return

        extractable_ok, extract_msg, extract_details = processor.validate_extractable(str(file_path))
        st.session_state.validation_status = extract_msg if not extractable_ok else st.session_state.validation_status

        if not report_extractability(extractable_ok, extract_msg, extract_details, continue_on_warning=False):
            return

        progress_bar = st.progress(0)
        st.session_state.uploaded_file_name = uploaded_file.name

        progress_bar.progress(20)
        extracted_text = extract_text_from_path(processor, file_path)
        if not extracted_text.strip():
            st.warning("⚠️ Document appears to be empty or image-only. Text extraction returned no content.")

        st.session_state.extracted_text = extracted_text
        progress_bar.progress(40)

        # Run validation rules on the extracted text to determine if review may proceed
        ai_confidence_score = 0.75 if len(extracted_text) > 250 else 0.45
        st.session_state.validation_confidence_score = ai_confidence_score
        st.session_state.validation_results = evaluate_validation_rules(
            extracted_text,
            st.session_state.document_title or "",
            "",
            st.session_state.metadata or {},
            ai_confidence_score,
            uploaded_file.name,
        )
        # store a canonical summary to avoid inconsistent counting in UI
        st.session_state.validation_summary = summarize_rule_results(st.session_state.validation_results)
        # Consider validation passed only if every validation rule explicitly PASSed.
        st.session_state.validation_passed = all(r.get("status") == "PASS" for r in st.session_state.validation_results)

        # If any validation rule failed, block the review step
        if not st.session_state.validation_passed:
            progress_bar.progress(40)
            st.error("❌ Validation checks failed — fix validation issues before running the review.")
            with st.expander("View validation findings", expanded=True):
                st.dataframe(
                    [
                        {
                            "Status": f"{ '✅' if r['status']=='PASS' else '⚠️' if r['status']=='WARNING' else '❌' } {r['status']}",
                            "ID": r["id"],
                            "Title": r["title"],
                            "Severity": r["severity"],
                            "Evidence": r["evidence"],
                            "Recommendation": r.get("recommendation", ""),
                        }
                        for r in st.session_state.validation_results
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            return

        st.session_state.metadata = processor.extract_metadata(str(file_path))
        progress_bar.progress(60)

        st.session_state.compliance_results = evaluate_compliance(extracted_text)
        st.session_state.rule_results = evaluate_document_rules(extracted_text, validation_results=st.session_state.validation_results)
        progress_bar.progress(80)

        st.session_state.chatbot = DocumentChatbot(extracted_text, openai_api_key=OPENAI_API_KEY)
        st.session_state.chat_history = []
        st.session_state.summary_text = ""
        st.session_state.review_completed = True
        progress_bar.progress(100)

        st.success("✅ GDP BOT review completed successfully.")
    except RuntimeError as e:
        st.error(f"❌ {e}")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
    finally:
        st.session_state.review_in_progress = False
        cleanup_temp_upload(file_path)


def render_main_tabs():
    render_top_insights()
    render_wizard()
    tabs = st.tabs(["🗂 Upload & Actions", "📊 Validation Dashboard", "✅ Review Insights", "💬 Chat & Intelligence"])

    with tabs[0]:
        render_upload_tab()
    with tabs[1]:
        render_validation_tab()
    with tabs[2]:
        render_review_tab()
    with tabs[3]:
        render_chat_tab()


def main():
    """Main application function"""
    initialize_session_state()
    display_sidebar_metadata()
    display_header()
    render_main_tabs()

    st.divider()
    with st.expander("🧹 Clear Session & Reset Interface", expanded=False):
        if st.button("Reset Workspace", key="workspace_reset", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.extracted_text = ""
            st.session_state.chatbot = None
            st.session_state.compliance_results = []
            st.session_state.rule_results = []
            st.session_state.metadata = {}
            st.session_state.validation_status = ""
            st.session_state.validation_passed = False
            st.session_state.validation_results = []
            st.session_state.validation_confidence_score = 0.0
            st.session_state.validation_completed = False
            st.session_state.review_completed = False
            st.session_state.uploaded_file_name = ""
            st.session_state.summary_text = ""
            st.rerun()


if __name__ == "__main__":
    main()
