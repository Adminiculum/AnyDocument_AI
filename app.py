"""
AnyDocument_AI — Chat with your documents using local Ollama models.

Supports PDF, DOCX, TXT and JSON files. Runs fully offline after installation.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import traceback
from typing import Optional
import atexit
import shutil

import ollama
import pandas as pd
import PyPDF2
import streamlit as st
from docx import Document

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Use a temporary directory for datasets
TEMP_DIR = tempfile.mkdtemp(prefix="anydocument_")
DATASET_FILE = os.path.join(TEMP_DIR, "dataset.csv")
MAX_CONTEXT_CHARS = 8_000
SYSTEM_PROMPT = (
    "You are an expert Document Analysis Assistant. "
    "You have been given the content of one or more documents. "
    "Answer the user's questions based solely on that content. "
    "If the answer cannot be found in the documents, say so clearly."
)

# ---------------------------------------------------------------------------
# Cleanup function for temporary directory
# ---------------------------------------------------------------------------

def cleanup_temp_dir():
    """Delete the temporary directory when the application exits."""
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"Cleaned up temporary directory: {TEMP_DIR}")
        except Exception as e:
            print(f"Error cleaning up temporary directory: {e}")

# Register cleanup function to run on exit
atexit.register(cleanup_temp_dir)

# ---------------------------------------------------------------------------
# Page configuration (must be the very first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AnyDocument AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load external CSS
# ---------------------------------------------------------------------------

def load_css():
    """Load external CSS file."""
    with open("style.css", "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

# Ensure temporary directory exists
os.makedirs(TEMP_DIR, exist_ok=True)


def _init_session_state() -> None:
    """Initialise all required session-state keys with safe defaults."""
    defaults: dict = {
        "df": pd.DataFrame(),
        "chat": [],
        "show_data": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session_state()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_model_list() -> list[str]:
    """Return the list of locally available Ollama models.

    Returns an empty list and surfaces an error if the ``ollama`` CLI is
    unavailable or returns an unexpected format.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        lines = result.stdout.splitlines()
        # Skip the header line ("NAME   ID   SIZE   MODIFIED")
        models = [
            line.split()[0]
            for line in lines[1:]
            if line.strip() and not line.startswith("NAME")
        ]
        return models
    except FileNotFoundError:
        st.error(
            "Ollama is not installed or not on PATH. "
            "Please run `setup.sh` first."
        )
    except subprocess.TimeoutExpired:
        st.error("Timed out while fetching the Ollama model list.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unexpected error fetching model list: {exc}")
    return []


def extract_text_from_file(uploaded_file) -> Optional[str]:
    """Extract plain text from an uploaded Streamlit file object.

    Parameters
    ----------
    uploaded_file:
        A Streamlit ``UploadedFile`` object.

    Returns
    -------
    str | None
        The extracted text, or ``None`` if extraction failed.
    """
    filename: str = uploaded_file.name
    extension: str = os.path.splitext(filename)[1].lower()

    try:
        if extension == ".pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            return "".join(
                page.extract_text() or "" for page in reader.pages
            )

        if extension == ".docx":
            doc = Document(uploaded_file)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)

        if extension == ".txt":
            return uploaded_file.read().decode("utf-8")

        if extension == ".json":
            payload = json.load(uploaded_file)
            return json.dumps(payload, indent=2, ensure_ascii=False)

        st.warning(
            f"Unsupported file type '{extension}' for '{filename}'. Skipping."
        )
        return None

    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not process '{filename}': {exc}")
        return None


def build_context(dataframe: pd.DataFrame) -> str:
    """Concatenate document contents into a single context string.

    The result is capped at ``MAX_CONTEXT_CHARS`` to stay within typical
    model context windows.
    """
    combined = "\n\n---\n\n".join(dataframe["content"].astype(str))
    if len(combined) > MAX_CONTEXT_CHARS:
        combined = (
            combined[:MAX_CONTEXT_CHARS] + "\n\n[... content truncated ...]"
        )
    return combined


def ask_model(question: str, model: str, context: str) -> str:
    """Send a question to the selected Ollama model and return the answer.

    Parameters
    ----------
    question:
        The user's natural-language question.
    model:
        The Ollama model identifier (e.g. ``"phi3:mini"``).
    context:
        Pre-built document context string.

    Returns
    -------
    str
        The model's response, or an error message string.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Here are the document contents you should reference:\n\n"
                f"{context}"
            ),
        },
        {"role": "user", "content": question},
    ]
    try:
        response = ollama.chat(model=model, messages=messages)
        return response.message.content.strip()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error while querying model '{model}': {exc}")
        traceback.print_exc()
        return f"An error occurred: {exc}"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## Configuration")
    st.markdown("---")

    # Model selector
    available_models = get_model_list()
    if available_models:
        selected_model: str = st.selectbox(
            "AI Model",
            options=available_models,
            help="Choose a locally installed Ollama model.",
        )
    else:
        st.warning("No models found. Run `ollama pull <model>` first.")
        selected_model = ""

    st.markdown("---")

    # File uploader
    st.markdown("### Upload Documents")
    uploaded_files = st.file_uploader(
        "Supported: PDF, DOCX, TXT, JSON",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "json"],
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) ready")
        for uf in uploaded_files:
            ext = os.path.splitext(uf.name)[1].upper().lstrip(".")
            icon_map = {"PDF": "📕", "DOCX": "📘", "TXT": "📄", "JSON": "🗂️"}
            icon = icon_map.get(ext, "📎")
            st.markdown(f"{icon} `{uf.name}`")
    else:
        st.info("No files uploaded yet.")

    st.markdown("---")

    # Process button - FIXED: replaced use_container_width with width
    process_clicked = st.button(
        "Process and Save",
        type="primary",
        width="stretch",  # This replaces use_container_width=True
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#bbf7d0'>AnyDocument AI runs fully offline "
        "after installation. Powered by "
        "<a href='https://ollama.com' style='color:#86efac'>Ollama</a>.</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main area — Hero header
# ---------------------------------------------------------------------------

st.markdown(
    '<p class="hero-title">AnyDocument AI</p>'
    '<p class="hero-subtitle">Upload documents, select a local AI model, '
    "and start asking questions — entirely offline.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Process uploaded files
# ---------------------------------------------------------------------------

if process_clicked:
    if not uploaded_files:
        st.error("Please upload at least one file before processing.")
    else:
        records: list[dict] = []
        progress_bar = st.progress(0, text="Processing files...")

        for idx, uf in enumerate(uploaded_files):
            progress_bar.progress(
                (idx + 1) / len(uploaded_files),
                text=f"Processing {uf.name}...",
            )
            text = extract_text_from_file(uf)
            if text:
                records.append({"name": uf.name, "content": text})

        progress_bar.empty()

        if records:
            st.session_state.df = pd.DataFrame(records)
            st.session_state.df.to_csv(DATASET_FILE, index=False)
            st.session_state.show_data = True
            st.success(
                f" {len(records)} file(s) processed and saved to temporary storage."
            )
            st.rerun()
        else:
            st.error(
                "No valid content could be extracted from the uploaded files."
            )

# ---------------------------------------------------------------------------
# Processed data preview
# ---------------------------------------------------------------------------

if st.session_state.show_data and not st.session_state.df.empty:
    with st.expander("Processed Document Preview", expanded=False):
        preview_df = st.session_state.df.copy()
        preview_df["content"] = preview_df["content"].str[:300] + "..."
        # FIXED: replaced use_container_width with width
        st.dataframe(preview_df, width="stretch")

        col_a, col_b = st.columns(2)
        col_a.metric("Documents loaded", len(st.session_state.df))
        total_chars = int(st.session_state.df["content"].str.len().sum())
        col_b.metric("Total characters", f"{total_chars:,}")

# ---------------------------------------------------------------------------
# Q&A section
# ---------------------------------------------------------------------------

if not st.session_state.df.empty:
    st.markdown("---")
    st.markdown("### Ask a Question")

    with st.form(key="qa_form", clear_on_submit=True):
        user_question: str = st.text_area(
            "Your question",
            placeholder="e.g. What are the main conclusions of the report?",
            height=80,
            label_visibility="collapsed",
        )
        submit = st.form_submit_button("Ask", type="primary")

    if submit:
        if not user_question.strip():
            st.warning("Please enter a question.")
        elif not selected_model:
            st.error(
                "No model selected. Please install an Ollama model first."
            )
        else:
            with st.spinner(f"Thinking with **{selected_model}**..."):
                context = build_context(st.session_state.df)
                answer = ask_model(user_question.strip(), selected_model, context)
            st.session_state.chat.append((user_question.strip(), answer))
            st.rerun()

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

if st.session_state.chat:
    st.markdown("---")
    st.markdown("### Conversation History")

    # Display newest messages first
    for user_msg, assistant_msg in reversed(st.session_state.chat):
        with st.chat_message("user"):
            st.write(user_msg)
        with st.chat_message("assistant"):
            st.write(assistant_msg)

    if st.button("Clear conversation"):
        st.session_state.chat = []
        st.rerun()

elif st.session_state.df.empty:
    # Onboarding hint shown when no documents are loaded yet
    st.markdown(
        """
        <div class="card">
        <h4>Getting started</h4>
        <ol>
          <li>Upload one or more documents using the <strong>sidebar</strong>.</li>
          <li>Click <strong>Process and Save</strong> to extract their content.</li>
          <li>Select an AI model from the dropdown.</li>
          <li>Type your question and click <strong>Ask</strong>.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
