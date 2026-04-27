from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag2 import process_file, query_rag
from db import init_db, check_connection
from contextlib import asynccontextmanager
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    success = init_db()
    if success:
        logger.info("Database initialized successfully.")
    else:
        logger.error("Database initialization failed.")
    yield
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan)

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.get("/health")
async def health_check():
    db_ok = check_connection()
    return {
        "status": "online",
        "database": "connected" if db_ok else "disconnected"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    try:
        content = await file.read()
        logger.info(f"Processing file: {file.filename}")
        success = process_file(content, file.filename)
        if success:
            return {"message": f"File '{file.filename}' uploaded and processed successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to process document content.")
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.post("/ask")
async def ask_question(query: Question):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        answer = query_rag(query.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
