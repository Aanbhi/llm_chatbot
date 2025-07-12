from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import os

class RAGChatEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0)

    def process_files_and_query(self, user_input, docs_path="uploads"):
        documents = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        for file in os.listdir(docs_path):
            if file.endswith(".txt"):
                loader = TextLoader(os.path.join(docs_path, file))
                documents += splitter.split_documents(loader.load())

        if not documents:
            return "Please upload at least one file to analyze."

        vectorstore = FAISS.from_documents(documents, self.embeddings)
        retriever = vectorstore.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)

        return qa_chain.run(user_input)