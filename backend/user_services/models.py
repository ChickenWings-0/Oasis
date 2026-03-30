# SQLAlchemy User model
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from backend.user_services.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    __allow_unmapped__ = True  # Allow unmapped columns for Pydantic v2 compatibility

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    auth_provider = Column(String(20), default="local", nullable=False)
    google_sub = Column(String(255), unique=True, index=True, nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"