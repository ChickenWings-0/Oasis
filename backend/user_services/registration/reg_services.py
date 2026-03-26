# Registration business logic
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from backend.user_services.models import User
from backend.user_services.schemas import UserRegister, UserProfile
from backend.user_services.jwt.pass_handler import PasswordHandler

class RegistrationService:
    """Handle user registration logic"""
    
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> UserProfile:
        """ Register a new user """
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            ).first()
            
            if existing_user:
                if existing_user.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            
            # Hash password
            hashed_password = PasswordHandler.hash_password(user_data.password)
            
            # Create new user
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                is_active=True
            )
            
            # Add to database
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return UserProfile.from_orm(db_user)
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed. Email or username may already exist."
            )
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration"
            )