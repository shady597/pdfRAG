from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag2 import process_file, query_rag
from db import init_db
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

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

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    try:
        content = await file.read()
        success = process_file(content, file.filename)
        if success:
            return {"message": f"File '{file.filename}' uploaded and processed successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to process document.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/ask")
async def ask_question(query: Question):
    try:
        answer = query_rag(query.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
