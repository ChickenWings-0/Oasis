# Token creation & verification
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import uuid
from fastapi import HTTPException, status

import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
if SECRET_KEY == "change-me-in-production":
    import warnings
    warnings.warn(
        "JWT_SECRET_KEY is not set. Using default insecure key. "
        "Set JWT_SECRET_KEY environment variable in production.",
        RuntimeWarning
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class JWTHandler:
    """Handle JWT token creation and verification"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """ Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add unique JWT ID and expiration to ensure token uniqueness
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4()),  # Unique JWT ID for each token
            "iat": datetime.now(timezone.utc)  # Issued at timestamp
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """ Verify and decode JWT token """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )