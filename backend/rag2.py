import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from db import get_vector_store
import tempfile

def process_file(file_content, filename):
    """Processes uploaded file content and adds to vector store."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path)
        
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)
        
        vector_store = get_vector_store()
        vector_store.add_documents(splits)
        
        return True
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def query_rag(question):
    """Queries the RAG pipeline for an answer."""
    vector_store = get_vector_store()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
    )
    
    result = qa_chain.invoke({"query": question})
    return result["result"]
