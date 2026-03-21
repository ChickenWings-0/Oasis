"""
Auth Dependency - JWT-based authentication

Handles token validation and user extraction.
Supports both JWT tokens and dev mode with X-User-ID header.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional
import jwt
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
        self.user_id = user_id
        self.email = email or f"user{user_id}@example.com"


# JWT Configuration
JWT_SECRET_KEY = "your-secret-key"  # TODO: Load from env
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(user_id: int, email: str) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        JWT token string
    """
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
    
    Args:
        token: JWT token string
        
    Returns:
        UserClaims with decoded user info
        
    Raises:
        HTTPException: If token invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )
        
        return UserClaims(user_id=user_id, email=email)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[int] = Header(None)
) -> CurrentUser:
    """
    Get current user from JWT token or dev header.
    
    Priority:
    1. Authorization: Bearer <token> (production)
    2. X-User-ID header (development/testing)
    
    Args:
        authorization: Authorization header with Bearer token
        x_user_id: User ID header (for development)
        
    Returns:
        CurrentUser object with user_id and email
        
    Raises:
        HTTPException: If not authenticated
    """
    # Try JWT token first
    if authorization:
        try:
            # Extract token from "Bearer <token>"
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid auth scheme")
            
            claims = verify_token(token)
            return CurrentUser(user_id=claims.user_id, email=claims.email)
        
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid authorization header: {str(e)}"
            )
    
    # Fallback to dev mode header
    if x_user_id is not None:
        return CurrentUser(user_id=x_user_id)
    
    # No auth found
    raise HTTPException(
        status_code=401,
        detail="Not authenticated. Provide 'Authorization: Bearer <token>' header or 'X-User-ID' header."
    )
