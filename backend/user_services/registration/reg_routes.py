# Registration endpoints
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.user_services.database import get_db
from backend.user_services.schemas import UserRegister, UserProfile, ErrorResponse
from backend.user_services.registration.reg_services import RegistrationService

router = APIRouter(
    prefix="/api/auth/register",
    tags=["registration"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

@router.post(
    "",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password"
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """ Register a new user"""
    
    return RegistrationService.register_user(user_data, db)