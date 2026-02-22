#!/bin/bash

# Update package list and install Python 3 and pip
sudo apt update
sudo apt install -y python3 python3-pip

# Install required Python libraries
pip3 install streamlit pandas PyPDF2 python-docx

# Install Ollama (Make sure you have curl or wget installed)
if [ "$(uname)" == "Linux" ]; then
    curl -sSfL https://ollama.com/download.sh | sh
fi

# Download and install models
ollama pull qwen:0.5
ollama pull phi3:mini
