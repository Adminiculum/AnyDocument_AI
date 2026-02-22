Project Title: AnyDocument_AI

Description:
AnyDocument_AI is a powerful Streamlit application that enables users to upload a variety of document types (PDF, DOCX, TXT, JSON) and interact with them using local AI models. Leveraging the capabilities of Python and the Ollama framework, this application allows users to seamlessly ask questions about their uploaded documents.

One of the standout features of this project is that it functions completely offline after installation, making it a reliable tool for users who require local processing without the need for an internet connection. This is particularly advantageous for working in environments with poor or restricted internet access.

To run this application optimally, it is recommended that the device has at least 16GB of RAM. While it can technically operate with 8GB of RAM, performance will be significantly slower, affecting the user experience.

Models Included:
- Phi3:mini Microsoft model that is reliable and performs very well for a variety of tasks.
- Qwen:0.5 A smaller and quicker model but not as powerful as Phi3.

Users can also install additional models to suit their computer's specifications. Visit [Ollama's model search](https://ollama.com/search) to explore more options.

Features:
- Upload various document formats (PDF, DOCX, TXT, JSON).
- Ask questions related to the content of the uploaded documents.
- Utilize local AI models for data processing and responses.
- Fully functional without internet connectivity after installation.

Requirements:
- Python 3.7 or higher
- Streamlit
- Pandas
- PyPDF2
- python-docx
- Ollama (with qwen 0.5 and phi3 models)
- Minimum 16GB of RAM (8GB is feasible but slow)

Installation Instructions:
1. Clone the repository:
  
   git clone <repository-url>
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

Contributing:
If you wish to contribute to the project, please fork the repository and create a pull request with your changes.
