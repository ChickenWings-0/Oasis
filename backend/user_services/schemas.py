# Pydantic schemas
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Registration Schema
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


# Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        }


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., min_length=10)

    class Config:
        json_schema_extra = {
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ij..."
            }
        }


# Token Response Schema
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2024-01-15T10:30:00"
            }
        }


# User Profile Schema
class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


# User Update Schema
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "jane_doe"
            }
        }


# Error Response Schema
class ErrorResponse(BaseModel):
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials"
            }
        }