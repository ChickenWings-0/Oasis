from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.user_services.database import get_db
from backend.user_services.schemas import GoogleAuthRequest, Token, ErrorResponse
from backend.user_services.login.google_services import GoogleAuthService

router = APIRouter(
    prefix="/api/auth/google",
    tags=["google-auth"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    }
)


@router.get(
    "/config",
    status_code=status.HTTP_200_OK,
    summary="Get Google sign-in config",
    description="Returns Google client configuration required by frontend sign-in widget"
)
def get_google_config():
    return {"client_id": GoogleAuthService.get_google_client_id()}


@router.post(
    "",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Google sign-in",
    description="Authenticate user with Google ID token and return JWT token"
)
def google_sign_in(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    return GoogleAuthService.authenticate_with_google(payload.id_token, db)
