# ChatGPT Clone with RAG, Vector Embeddings, and LLM

This project is a lightweight and deployable ChatGPT-style chatbot application built with the following features:
- Large Language Model (LLM) powered responses using the OpenAI API
- Retrieval-Augmented Generation (RAG) with FAISS vector search
- Vector embeddings for document context
- Upload support for `.txt` files to enhance chat understanding
- Streamlit-based web user interface
- Chat memory and history functionality
- Docker support for local execution
- Render-ready deployment

---

## Features

1. **Text-based Conversation**  
   Users can chat with the AI assistant in a conversational interface.

2. **Contextual Document Upload**  
   Upload `.txt` files to provide relevant content for the chatbot to reference via RAG.

3. **On-the-fly Embedding and Search**  
   Documents are embedded using the OpenAI Embeddings API and searched using FAISS.

4. **Chat History**  
   Previous interactions are stored per session and displayed chronologically.

5. **Clear Chat History**  
   Users can reset the conversation at any time using a dedicated sidebar control.

---

## Technologies Used

- Python 3.10
- Streamlit
- LangChain
- OpenAI API
- FAISS
- Docker

---

## Project Structure

chatgpt_clone/

├── app/

│ ├── rag_engine.py # Handles RAG and vector search

│ ├── memory.py # Session-based chat history

│ └── utils.py # Utility functions (optional extensions)

├── uploads/ # Temporary document upload storage

├── vectorstore/ # Reserved for FAISS persistence (optional)

├── main.py # Streamlit app entrypoint

├── requirements.txt # Python dependencies

├── Dockerfile # Container configuration

└── .env # OpenAI API key (not to be committed)

---

## Environment Variables

Create a `.env` file with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_key_here

Do not commit this file to version control. You can also set it through your Render dashboard or Docker environment.

Running Locally

Prerequisites

1. Python 3.10+

2. pip

Steps

git clone https://github.com/your-username/chatgpt_clone.git
cd chatgpt_clone

python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows

pip install -r requirements.txt

streamlit run main.py

Docker Deployment (Local)

Build and run the container:

docker build -t chatgpt-clone .
docker run -p 8501:8501 chatgpt-clone

Access the app at http://localhost:8501

Render Deployment (Cloud)
Push the code to a GitHub repository.

Create a new Web Service at Render.

Connect your repository and configure:

Build Command: pip install -r requirements.txt

Start Command: streamlit run main.py --server.port=10000 --server.enableCORS=false

Python Version: 3.10

Environment Variable: OPENAI_API_KEY=your_openai_key_here

Render will automatically build and deploy the application.

Notes and Considerations
Only .txt files are supported for file upload to maintain lightweight memory usage.

This setup avoids storing embeddings or large files on disk to stay within Render’s free-tier RAM and storage limits.

For persistent vector storage, you can optionally extend rag_engine.py using FAISS .save_local() and .load_local() methods.
