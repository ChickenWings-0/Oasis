# Login endpoints
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.user_services.database import get_db
from backend.user_services.schemas import UserLogin, Token, ErrorResponse
from backend.user_services.login.log_services import LoginService

router = APIRouter(
    prefix="/api/auth/login",
    tags=["login"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    }
)

@router.post(
    "",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, returns JWT token"
)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and get JWT token
    
    Returns JWT access token to be used in subsequent requests
    """
    return LoginService.authenticate_user(login_data, db)