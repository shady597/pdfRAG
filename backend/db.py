import os
import logging
from sqlalchemy import create_engine, text
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Database connection string - expects postgresql://user:pass@host:port/dbname
DB_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "documents"

# Global instance for embeddings to avoid re-initialization
_embeddings = None

def get_embeddings():
    """Returns a cached instance of OpenAIEmbeddings."""
    global _embeddings
    if _embeddings is None:
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not found in environment variables.")
        _embeddings = OpenAIEmbeddings()
    return _embeddings

def init_db():
    """Ensures the pgvector extension exists and the database is reachable."""
    if not DB_URL:
        logger.error("DATABASE_URL not set. Vector store will not be available.")
        return False

    try:
        # We use a standard engine to ensure the extension is enabled
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            # PostgreSQL requires the extension to be created before use
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("✅ Database initialized (vector extension enabled).")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def check_connection():
    """Simple health check for the database."""
    try:
        if not DB_URL:
            return False
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_vector_store():
    """Initializes and returns the PGVector store instance."""
    if not DB_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
        
    return PGVector(
        connection=DB_URL,
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )
