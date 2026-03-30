import os
import re
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from backend.user_services.models import User
from backend.user_services.schemas import Token
from backend.user_services.jwt.pass_handler import PasswordHandler
from backend.user_services.jwt.jwt_handler import JWTHandler


class GoogleAuthService:
    """Handle Google sign-in and account linking."""

    @staticmethod
    def get_google_client_id() -> str:
        return os.getenv("GOOGLE_CLIENT_ID", "")

    @staticmethod
    def authenticate_with_google(google_id_token: str, db: Session) -> Token:
        client_id = GoogleAuthService.get_google_client_id()

        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_CLIENT_ID is not configured"
            )

        try:
            id_info = id_token.verify_oauth2_token(
                google_id_token,
                requests.Request(),
                client_id,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        issuer = id_info.get("iss")
        if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = id_info.get("email")
        email_verified = id_info.get("email_verified", False)
        google_sub = id_info.get("sub")

        if not email or not google_sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google token missing required claims"
            )

        if not email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google email is not verified"
            )

        user = db.query(User).filter(User.google_sub == google_sub).first()

        if not user:
            user = db.query(User).filter(User.email == email).first()

        if user:
            user.google_sub = google_sub
            user.auth_provider = "google"
            if id_info.get("given_name"):
                user.first_name = id_info.get("given_name")
            if id_info.get("family_name"):
                user.last_name = id_info.get("family_name")
        else:
            username = GoogleAuthService._build_unique_username(email, db)
            temp_password = PasswordHandler.hash_password(str(uuid.uuid4()))
            user = User(
                username=username,
                email=email,
                hashed_password=temp_password,
                auth_provider="google",
                google_sub=google_sub,
                first_name=id_info.get("given_name", ""),
                last_name=id_info.get("family_name", ""),
                is_active=True,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
        }

        access_token = JWTHandler.create_access_token(data=token_data)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
        )

    @staticmethod
    def _build_unique_username(email: str, db: Session) -> str:
        # Keep username deterministic and URL-safe based on email local-part.
        base = email.split("@")[0].lower().strip()
        sanitized = re.sub(r"[^a-z0-9_]", "_", base)
        candidate = sanitized[:45] if len(sanitized) > 45 else sanitized

        if not candidate:
            candidate = "google_user"

        if db.query(User).filter(User.username == candidate).first() is None:
            return candidate

        suffix = 1
        while True:
            trial = f"{candidate}_{suffix}"
            if db.query(User).filter(User.username == trial).first() is None:
                return trial
            suffix += 1
