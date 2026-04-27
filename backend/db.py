import os
from sqlalchemy import create_engine, text
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Database connection string
DB_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "documents"

def init_db():
    """Ensures the pgvector extension exists and the database is ready."""
    if not DB_URL:
        print("Skipping DB initialization: DATABASE_URL not set.")
        return

    try:
        # Use a temporary engine to run the extension creation
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        print("✅ Database initialized (vector extension enabled).")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

def get_vector_store():
    """Initializes and returns the PGVector store."""
    if not DB_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
        
    embeddings = OpenAIEmbeddings()
    
    vector_store = PGVector(
        connection=DB_URL,
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )
    return vector_store
