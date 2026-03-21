# Database connection setup
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed, using os.getenv")

# PostgreSQL database URL
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/auth_db"
)

logger.info(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    echo=False,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()