# Project: PDF RAG System

A full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload PDF/TXT documents and query their content using AI.

## Architecture Overview

- **Frontend:** React + Vite + TailwindCSS (inferred from `Frontend/` and `index.css`).
- **Backend:** FastAPI (Python 3.14+) providing a RESTful API.
- **Vector Database:** PostgreSQL with the `pgvector` extension, managed via SQLAlchemy and LangChain's `PGVector`.
- **RAG Engine:** LangChain with OpenAI's GPT-3.5-Turbo and OpenAI Embeddings.

## Directory Structure

- `/backend`: Python FastAPI server, database logic (`db.py`), and RAG pipeline (`rag2.py`).
- `/Frontend`: React application managed by Vite.

## Tech Stack

- **Languages:** Python, JavaScript (React).
- **Backend Framework:** FastAPI.
- **AI/LLM Tools:** LangChain, OpenAI, OpenAI Embeddings.
- **Database:** PostgreSQL + PGVector.
- **Frontend Build Tool:** Vite.

## Building and Running

### Prerequisites
- Python 3.14+
- Node.js & npm
- PostgreSQL database with `pgvector` installed.

### Backend Setup
1. Navigate to `/backend`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` (use `.env.example` as a template):
   - `DATABASE_URL`: Connection string for PostgreSQL.
   - `OPENAI_API_KEY`: Your OpenAI API key.
4. Run the server:
   ```bash
   python main.py
   ```
   *The backend runs on `http://localhost:8000`.*

### Frontend Setup
1. Navigate to `/Frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *The frontend runs on `http://localhost:5173`.*

## Development Conventions

- **Environment Variables:** Always use `.env` for secrets (API keys, DB URLs). Ensure `.env` is ignored by Git.
- **Logging:** The backend uses standard Python `logging` to track file processing and RAG queries.
- **CORS:** The backend is pre-configured to allow requests from `http://localhost:5173`.
- **Database Initialization:** The backend automatically ensures the `vector` extension exists in PostgreSQL on startup via `init_db()`.
- **API Models:** Pydantic is used for request/response validation in the backend.

## Key API Endpoints

- `GET /health`: Checks database connectivity.
- `POST /upload`: Uploads and processes a PDF/TXT file into the vector store.
- `POST /ask`: Queries the RAG system with a text question.
