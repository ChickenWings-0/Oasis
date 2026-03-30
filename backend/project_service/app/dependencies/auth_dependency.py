"""
Auth Dependency - JWT-based authentication

Handles token validation and user extraction.
Requires JWT tokens via Authorization header.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta
from pydantic import BaseModel


class UserClaims(BaseModel):
    """User info extracted from JWT token"""
    user_id: int
    email: str
    iat: Optional[int] = None  # issued at
    exp: Optional[int] = None  # expiration


class CurrentUser:
    """Current authenticated user"""
    def __init__(self, user_id: int, email: Optional[str] = None):
        self.id = user_id
        self.email = email or f"user{user_id}@example.com"


# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(user_id: int, email: str) -> str:
   # Create JWT access token

    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> UserClaims:
    """
    Verify and decode JWT token
   
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        raw_user_id = payload.get("user_id") or payload.get("sub")
        email = payload.get("email")
        
        if raw_user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user identifier"
            )

        try:
            user_id = int(raw_user_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=401,
                detail="Invalid token: invalid user identifier"
            )
        
        return UserClaims(user_id=user_id, email=email)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> CurrentUser:
    """
    Get current user from JWT token.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Provide 'Authorization: Bearer <token>' header."
        )

    try:
        scheme, token = authorization.split(maxsplit=1)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )

    claims = verify_token(token)
    return CurrentUser(user_id=claims.user_id, email=claims.email)
