#!/bin/bash

# Update package list and install Python 3 and pip
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl

# Create a virtual environment with the new name
python3 -m venv AIvenv

# Activate the virtual environment
source AIvenv/bin/activate

# Install required Python libraries within the virtual environment
pip install streamlit pandas PyPDF2 python-docx ollama

# Install Ollama
if [ "$(uname)" == "Linux" ]; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Download and install models
ollama pull qwen:0.5
ollama pull phi3:mini

# Deactivate the virtual environment
deactivate
