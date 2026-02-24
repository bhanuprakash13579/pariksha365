from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth_schema import Token, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
from app.schemas.user_schema import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new user.
    """
    user = await auth_service.create_user(db, user_in)
    return user

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    return await auth_service.login_user(db, email=login_data.email, password=login_data.password)

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Request a password reset token. In production, this would be emailed.
    """
    token = await auth_service.forgot_password(db, email=body.email)
    return MessageResponse(message=f"Password reset token: {token}")

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Reset password using the token received from forgot-password.
    """
    await auth_service.reset_password(db, token=body.token, new_password=body.new_password)
    return MessageResponse(message="Password has been reset successfully.")
