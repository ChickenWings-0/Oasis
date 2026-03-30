# Profile endpoints
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.user_services.database import get_db
from backend.user_services.models import User
from backend.user_services.schemas import UserProfile, UserUpdate, ErrorResponse
from backend.user_services.dependencies import get_current_user
from backend.user_services.profiles.prof_services import ProfileService
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/profile",
    tags=["profile"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Not found"},
    }
)

# Schema for password change request
class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "OldPass123!",
                "new_password": "NewPass123!"
            }
        }

@router.get(
    "",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Retrieve current user's profile information"
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information
    
    Requires valid JWT token in Authorization header
    """
    return ProfileService.get_user_profile(current_user.id, db)

@router.put(
    "",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update user profile information (name, username)"
)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    
    Requires valid JWT token in Authorization header
    """
    return ProfileService.update_user_profile(current_user.id, update_data, db)

@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user's password"
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user's password
    
    Requires valid JWT token in Authorization header
    """
    return ProfileService.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password,
        db
    )

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete account",
    description="Delete user's account permanently"
)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account permanently
    
    Requires valid JWT token in Authorization header
    """
    return ProfileService.delete_user_account(current_user.id, db)