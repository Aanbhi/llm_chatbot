import streamlit as st
from app.rag_engine import RAGChatEngine
from app.memory import ChatMemory
import os
import shutil

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="ChatGPT Clone", layout="wide")
st.title("💬 ChatGPT-style Bot with RAG")

if "memory" not in st.session_state:
    st.session_state.memory = ChatMemory()

if "engine" not in st.session_state:
    st.session_state.engine = RAGChatEngine()

def clear_uploads():
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")
    os.makedirs("uploads")

clear_uploads()

st.sidebar.header("Upload Files (.txt only)")
uploaded_files = st.sidebar.file_uploader("Upload text files", type=["txt"], accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        with open(os.path.join("uploads", file.name), "wb") as f:
            f.write(file.read())
    st.sidebar.success("Files uploaded.")

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.memory.clear()
    st.experimental_rerun()

user_input = st.chat_input("Ask your question...")
if user_input:
    st.session_state.memory.add_message("user", user_input)
    response = st.session_state.engine.process_files_and_query(user_input)
    st.session_state.memory.add_message("bot", response)

for msg in st.session_state.memory.get_history():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])