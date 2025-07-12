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

---

## Running Locally

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

---
