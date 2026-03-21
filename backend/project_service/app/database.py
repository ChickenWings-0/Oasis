from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Database URL
DATABASE_URL = settings.project_database_url

# Create engine with connection pooling
if settings.environment == "development":
    # Development: Use NullPool for simplicity
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        echo=True,  # Log SQL statements
        connect_args={"connect_timeout": 10}
    )
else:
    # Production: Use QueuePool with proper pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        connect_args={"connect_timeout": 10}
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency for getting database session in routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
