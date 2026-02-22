import streamlit as st
import pandas as pd
import PyPDF2
from docx import Document
import json
import ollama
import os
import subprocess
import traceback

# Create directory for datasets if it doesn't exist
os.makedirs("datasets", exist_ok=True)

def get_model_list():
    try:
        result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        model_list = result.stdout.splitlines()
        return [model.split()[0] for model in model_list if model]
    except Exception as e:
        st.error(f"Error fetching model list: {str(e)}")
        return []

def process_file(f):
    n = f.name
    st.write(f"Processing file: {n}")
    try:
        if n.endswith('.pdf'):
            r = PyPDF2.PdfReader(f)
            return "".join(page.extract_text() or "" for page in r.pages)
        elif n.endswith('.docx'):
            d = Document(f)
            return "\n".join(p.text for p in d.paragraphs)
        elif n.endswith('.txt'):
            return f.read().decode("utf-8")
        elif n.endswith('.json'):
            return json.dumps(json.load(f))
    except Exception as e:
        st.error(f"Error processing file {n}: {str(e)}")
    return ""

def qa(question, model):
    df = st.session_state.df
    ctx = "".join(df.content.astype(str))[:5000]  # Limit context to 5000 characters
    msg = [
        {"role": "system", "content": "You are an expert Data Analysis Assistant with access to a dataset. Your task is to provide answers based on that dataset only."},
        {"role": "user", "content": f"Here is the dataset you should reference:\n{ctx}"},
        {"role": "user", "content": f"{question}"}
    ]
    try:
        resp = ollama.chat(model=model, messages=msg)
        return resp.message.content.strip()
    except Exception as e:
        st.error(f"Error during QA with model {model}: {str(e)}")
        print(traceback.format_exc())
        return f"An error occurred: {str(e)}"

# Streamlit application title
st.title("AnyDocument_AI")

# File uploader widget
files = st.file_uploader("Upload PDF/DOCX/TXT/JSON", accept_multiple_files=True)

if files:
    st.success(f"{len(files)} file(s) uploaded!")
else:
    st.warning("Please upload some files.")

# Initialize session state for DataFrame and chat history
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'chat' not in st.session_state:
    st.session_state.chat = []

# Fetch available models
available_models = get_model_list()
selected_model = st.selectbox("Choose model:", available_models)

# Button to process uploaded files
if st.button("Process & Save"):
    data = []
    for f in files:
        result = process_file(f)
        if result:  # Only append if there is content
            data.append({"name": f.name, "content": result})

    if data:  # Ensure data is not empty
        st.session_state.df = pd.DataFrame(data)
        st.session_state.df.to_csv("datasets/dataset.csv", index=False)
        st.success("Saved datasets/dataset.csv")
        st.session_state['show_data'] = True  # Set flag to display data
        st.rerun()
    else:
        st.error("No valid data processed from the files.")

# Condition to display processed DataFrame
if 'show_data' in st.session_state and st.session_state['show_data']:
    st.subheader("Processed Data")
    st.dataframe(st.session_state.df)

# QA section
if len(st.session_state.df) > 0:
    col1, col2 = st.columns(2)

    with col1:
        q = st.text_input("Question:")

    with col2:
        if st.button("Ask", type="primary") and q:
            if selected_model:
                st.write(f"Using model: {selected_model}")
                a = qa(q, selected_model)
                st.session_state.chat.append((q, a))
                st.rerun()
            else:
                st.error("Please select a model before asking.")

# Display chat history
if st.session_state.chat:
    st.subheader("Chat History")
    for q, a in st.session_state.chat:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(a)
