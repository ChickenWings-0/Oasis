from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database
    project_database_url: str
    
    # Environment
    environment: str = "development"
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False


settings = Settings()
