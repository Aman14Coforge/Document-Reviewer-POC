"""UI Components Module - Streamlit UI helper functions"""

import streamlit as st

# Small HTML constants to keep templates maintainable
HEADER_HTML = """
<div style='background: linear-gradient(135deg, #ffffff 0%, #e9f2ff 100%); border-radius: 24px; padding: 32px; margin-bottom: 28px; box-shadow: 0 28px 90px rgba(16, 61, 140, 0.14);'>
    <div style='display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 24px;'>
        <div style='max-width: 720px;'>
            <div style='display: inline-flex; align-items: center; gap: 10px; margin-bottom: 18px;'>
                <span style='display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 18px; background: linear-gradient(135deg, #2b6ef6, #5eb2ff); color: #fff; font-weight: 700; font-size: 1.1rem;'>AI</span>
                <span style='padding: 10px 16px; border-radius: 999px; background: rgba(43, 110, 246, 0.12); color: #1d3b78; font-size: 0.95rem; font-weight: 700;'>Advanced Workflow</span>
            </div>
            <h1 style='margin: 0; font-size: 3rem; line-height: 1.02; color: #0d2d6f; letter-spacing: -0.04em;'>Document Extractor Chatbot</h1>
            <p style='margin: 18px 0 0; color: #475569; font-size: 1.05rem; max-width: 760px;'>Smart document OCR, compliance validation, rule review, and AI chat all in one elegant workspace.</p>
        </div>
        <div style='min-width: 280px; background: rgba(14, 58, 141, 0.95); border-radius: 24px; padding: 24px; color: #ffffff; box-shadow: 0 20px 40px rgba(14, 58, 141, 0.2);'>
            <div style='font-size: 0.8rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.88;'>AI-powered review</div>
            <div style='margin-top: 18px;'>
                <p style='margin: 0 0 14px; font-size: 1rem; line-height: 1.6;'>Upload documents, validate structure, inspect compliance, and ask questions about the content instantly.</p>
                <ul style='margin: 0; padding-left: 18px; color: rgba(255,255,255,0.9); line-height: 1.8;'>
                    <li>Fast OCR & text extraction</li>
                    <li>Rule and compliance analysis</li>
                    <li>Interactive chat insights</li>
                </ul>
            </div>
        </div>
    </div>                                
</div>
"""

SIDEBAR_HTML = """
<div style='background: linear-gradient(180deg, #f8fbff 0%, #e7efff 100%); border-radius: 22px; padding: 20px 18px; margin-bottom: 18px; box-shadow: 0 18px 45px rgba(18, 49, 111, 0.08);'>
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 14px;'>
        <span style='font-size: 1.2rem;'>⚙️</span>
        <div>
            <h3 style='margin:0; color:#11306f;'>Workspace</h3>
            <p style='margin: 6px 0 0; color:#3e516d; font-size:0.95rem;'>Your advanced review control panel.</p>
        </div>
    </div>
</div>
"""

def _ensure_session_state_defaults():
    """Ensure commonly used session keys exist with safe defaults."""
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("chatbot", None)
    st.session_state.setdefault("compliance_results", [])
    st.session_state.setdefault("validation_results", [])
    st.session_state.setdefault("extracted_text", "")

def display_header():
    """Display application header"""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar information and settings"""
    _ensure_session_state_defaults()

    with st.sidebar:
        st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

        st.markdown("## Overview")
        st.info("Upload and review documents with advanced OCR, compliance scoring, and AI-powered chat.")

        st.markdown("## Supported Formats")
        st.write("- PDF files (.pdf)")
        st.write("- Images (.jpg, .png, .bmp, .tiff)")
        st.write("- Text files (.txt)")
        st.write("- Word documents (.docx)")

        st.markdown("## Quick Tips")
        st.markdown("""
        - Use clear, high-resolution source documents.
        - Avoid scanned pages with heavy noise.
        - Add document titles and metadata for better context.
        - Run validation before full review.
        """)

        with st.expander("Rules and compliance details"):
            st.markdown("""
            Use the review panel to see:
            - rule-based compliance findings
            - extractability results
            - validation status and recommendations
            """)
            if 'compliance_results' in st.session_state and st.session_state.compliance_results:
                try:
                    st.table(st.session_state.compliance_results)
                except Exception:
                    for result in st.session_state.compliance_results:
                        st.markdown(f"**{result['id']}** - {result['title']}")
                        st.markdown(f"Status: {result['status']} | Severity: {result['severity']}")
            else:
                st.info("No compliance results available yet.")

        if 'validation_results' in st.session_state and st.session_state.validation_results:
            st.markdown("## Validation Status")
            validation_pass = sum(1 for r in st.session_state.validation_results if r.get('status') == 'PASS')
            validation_fail = sum(1 for r in st.session_state.validation_results if r.get('status') == 'FAIL')
            st.metric("Validation Passed", validation_pass)
            st.metric("Validation Failed", validation_fail)

        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("## Chat Summary")
            st.write(f"{len(st.session_state.chat_history)} messages")
            if st.button("Clear Chat", use_container_width=True, key="sidebar_clear_chat"):
                st.session_state.chat_history = []
                st.session_state.chatbot = None
                st.experimental_rerun()

def display_chat_interface():
    """Display chat interface for Q&A"""
    _ensure_session_state_defaults()

    # Chat history
    chat_container = st.container()

    with chat_container:
        # Display conversation history
        if st.session_state.chat_history:
            for i, (question, answer) in enumerate(st.session_state.chat_history):
                display_chat_message("user", question)
                display_chat_message("assistant", answer)

    # Chat input (use a form so Enter submits naturally)
    st.divider()

    with st.form("chat_form"):
        cols = st.columns([4, 1])
        with cols[0]:
            user_query = st.text_input(
                "Ask a question about your document:",
                placeholder="e.g., What is the main topic of this document?",
                label_visibility="collapsed"
            )
        with cols[1]:
            submitted = st.form_submit_button("Send")

        if submitted and user_query:
            if not st.session_state.chatbot:
                st.error("Chatbot not initialized. Please upload/initialize a document first.")
            else:
                try:
                    response = st.session_state.chatbot.generate_response(user_query)
                except Exception as exc:
                    st.error(f"Chatbot error: {exc}")
                else:
                    st.session_state.chat_history.append((user_query, response))
                    st.experimental_rerun()
    
    # Additional features
    st.divider()
    st.subheader("🛠️ Document Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Summary", use_container_width=True):
            if not st.session_state.chatbot:
                st.error("Chatbot not initialized.")
            else:
                try:
                    summary = st.session_state.chatbot.get_summary()
                except Exception as exc:
                    st.error(f"Error generating summary: {exc}")
                else:
                    st.info(f"**Summary:** {summary}")
    
    with col2:
        if st.button("🔑 Extract Key Terms", use_container_width=True):
            if not st.session_state.chatbot:
                st.error("Chatbot not initialized.")
            else:
                try:
                    key_terms = st.session_state.chatbot.get_key_terms()
                except Exception as exc:
                    st.error(f"Error extracting key terms: {exc}")
                else:
                    st.success(f"**Key Terms:** {', '.join(key_terms)}")
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.extracted_text = ""
            st.session_state.chatbot = None
            st.session_state.compliance_results = []
            st.experimental_rerun()


def display_chat_message(role: str, content: str):
    """
    Display a chat message
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
    """
    with st.chat_message(role):
        st.write(content)

def display_info_box(title: str, content: str, info_type: str = "info"):
    """
    Display an information box
    
    Args:
        title: Box title
        content: Box content
        info_type: 'info', 'success', 'warning', 'error'
    """
    if info_type == "info":
        st.info(f"**{title}** \n {content}")
    elif info_type == "success":
        st.success(f"**{title}** \n {content}")
    elif info_type == "warning":
        st.warning(f"**{title}** \n {content}")
    elif info_type == "error":
        st.error(f"**{title}** \n {content}")

def display_statistics(text: str):
    """
    Display text statistics
    
    Args:
        text: Text to analyze
    """
    lines = text.split("\n")
    words = text.split()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", len(text))
    with col2:
        st.metric("Words", len(words))
    with col3:
        st.metric("Lines", len([l for l in lines if l.strip()]))
    with col4:
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        st.metric("Avg Word Length", f"{avg_word_length:.1f}")
