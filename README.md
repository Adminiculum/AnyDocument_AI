 Project : AnyDocument_AI

 Description:
AnyDocument_AI is a powerful Streamlit application that enables users to upload a variety of document types (PDF, DOCX, TXT, JSON) and interact with them using local AI models. Leveraging the capabilities of Python and the Ollama framework, this application allows users to seamlessly ask questions about their uploaded documents.

One of the standout features of this project is that it functions completely offline after installation, making it a reliable tool for users who require local processing without the need for an internet connection. This is particularly advantageous for working in environments with poor or restricted internet access.

The application has been tested on Ubuntu 20.04 TLS, Debian, and Raspberry Pi, confirming that it works on any Debian-based distribution.

To run this application optimally, it is recommended that the device has at least 16GB of RAM. While it can technically operate with 8GB of RAM, performance will be significantly slower, affecting the user experience.

 Security Features:
- Complete data privacy - All processing is done locally on your machine
- Automatic file deletion - Uploaded documents are automatically and permanently deleted after each session ends
- No data retention - Files are not stored permanently and are removed from memory once processed
- Secure local processing - Your documents never leave your computer

 Models Included:
The setup script includes the following models with their recommended specifications:

- llama3.2:3b - Lightweight model requiring minimal resources
  - RAM: 4GB minimum
  - Storage: 2GB
  - CPU: Compatible with most systems

- qwen2.5:3b - Balanced performance model
  - RAM: 4GB minimum, 8GB recommended
  - Storage: 2.5GB
  - CPU: Multi-core processor recommended

Users can install additional models to suit their computer's specifications. Visit [Ollama's model search](https://ollama.com/search) to explore more options.

 Features:
- Upload various document formats (PDF, DOCX, TXT, JSON).
- Ask questions related to the content of the uploaded documents.
- Utilize local AI models for data processing and responses.
- Fully functional without internet connectivity after installation.
- Automatic file deletion after each session for enhanced privacy.
- Local processing only - no cloud upload or third-party services.

 Requirements:
- Python 3.7 or higher
- Streamlit
- Pandas
- PyPDF2
- python-docx
- Ollama
- Minimum 16GB of RAM (8GB is feasible but slow)

 Installation Instructions:
1. Clone the repository:
   
   git clone https://github.com/Adminiculum/AnyDocument_AI.git
   cd AnyDocument_AI

2. Make the setup and run scripts executable:
  
   chmod +x setup.sh
   chmod +x run.sh

3. Run the setup script to install dependencies and models:
   
   ./setup.sh

4. Run the Streamlit application:
   
   ./run.sh

 Usage:
- Upload your dataset files using the provided file uploader in the UI.
- Select the language model you wish to use from the dropdown menu.
- Ask questions about the data by typing them into the text input field and clicking the "Ask" button.
- Files are automatically deleted when you close the session or upload new ones.

 Contributing:
If you wish to contribute to the project, please fork the repository and create a pull request with your changes.
