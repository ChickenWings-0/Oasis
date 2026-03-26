# Profile business logic
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.user_services.models import User
from backend.user_services.schemas import UserProfile, UserUpdate
from backend.user_services.jwt.pass_handler import PasswordHandler

class ProfileService:
    """Handle user profile operations"""
    
    @staticmethod
    def get_user_profile(user_id: int, db: Session) -> UserProfile:
        """ Get user profile information """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile.from_orm(user)
    
    @staticmethod
    def update_user_profile(user_id: int, update_data: UserUpdate, db: Session) -> UserProfile:
        """ Update user profile information """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if new username is already taken by another user
        if update_data.username:
            existing_user = db.query(User).filter(
                (User.username == update_data.username) & (User.id != user_id)
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            user.username = update_data.username
        
        # Update other fields
        if update_data.first_name:
            user.first_name = update_data.first_name
        
        if update_data.last_name:
            user.last_name = update_data.last_name
        
        db.commit()
        db.refresh(user)
        
        return UserProfile.from_orm(user)
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str, db: Session) -> dict:
        """ Change user password """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not PasswordHandler.verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current password"
            )
        
        # Hash and update new password
        user.hashed_password = PasswordHandler.hash_password(new_password)
        db.commit()
        
        return {"detail": "Password changed successfully"}
    
    @staticmethod
    def delete_user_account(user_id: int, db: Session) -> dict:
        """ Delete user account """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        return {"detail": "Account deleted successfully"}