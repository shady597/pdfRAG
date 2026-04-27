import os
import logging
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from db import get_vector_store

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_file(file_content, filename):
    """Processes uploaded file content and adds to vector store."""
    suffix = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        if suffix == '.pdf':
            loader = PyPDFLoader(tmp_path)
        elif suffix == '.txt':
            loader = TextLoader(tmp_path)
        else:
            logger.error(f"Unsupported file type: {suffix}")
            return False
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document pages/sections from {filename}")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(splits)} chunks")
        
        vector_store = get_vector_store()
        vector_store.add_documents(splits)
        logger.info(f"Successfully added {len(splits)} chunks to vector store")
        
        return True
    except Exception as e:
        logger.error(f"Error processing file {filename}: {str(e)}")
        return False
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def query_rag(question):
    """Queries the RAG pipeline for an answer using modern LCEL chains."""
    try:
        vector_store = get_vector_store()
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        
        # Define the system prompt
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise.\n\n"
            "{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        
        # Create the chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(vector_store.as_retriever(), question_answer_chain)
        
        logger.info(f"Querying RAG with: {question}")
        response = rag_chain.invoke({"input": question})
        
        return response["answer"]
    except Exception as e:
        logger.error(f"Error in query_rag: {str(e)}")
        raise e
