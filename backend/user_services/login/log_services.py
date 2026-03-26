# Login business logic
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.user_services.models import User
from backend.user_services.schemas import UserLogin, Token
from backend.user_services.jwt.pass_handler import PasswordHandler
from backend.user_services.jwt.jwt_handler import JWTHandler

class LoginService:
    """Handle user login logic"""
    
    @staticmethod
    def authenticate_user(login_data: UserLogin, db: Session) -> Token:
        """ Authenticate user and generate JWT toke """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        if user.auth_provider == "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses Google sign-in. Use /api/auth/google instead."
            )
        
        # Verify password
        if not PasswordHandler.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "username": user.username
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
            created_at=user.created_at
        )