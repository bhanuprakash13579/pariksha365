from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.schemas.auth_schema import Token, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse, GoogleLoginRequest, AppleLoginRequest
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

@router.post("/google", response_model=Token)
async def google_login(
    login_data: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    return await auth_service.authenticate_google_user(db, token=login_data.token)


@router.post("/apple", response_model=Token)
async def apple_login(
    login_data: AppleLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login or create a user via Apple Sign-In identity token."""
    return await auth_service.authenticate_apple_user(
        db,
        identity_token=login_data.identity_token,
        full_name=login_data.full_name,
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Request a password reset token. In production, this would be emailed.
    """
    await auth_service.forgot_password(db, email=body.email)
    return MessageResponse(message="If this email is registered, a password reset link has been sent.")

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

# Admin-only diagnostics for password-verification issues. The earlier version
# of this endpoint was unauthenticated and leaked the stored hash prefix, the
# bcrypt library version, and `is_active` for any email an attacker guessed.
# Now requires a valid admin session via get_current_admin_user.
@router.get("/debug-verify/{email}")
async def debug_verify(
    email: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    from sqlalchemy.future import select
    from app.models.user import User
    from app.core.security import verify_password, get_password_hash
    import bcrypt as _bcrypt

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        return {"found": False, "email": email}

    import os as _os
    test_password = _os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "")
    if not test_password:
        return {"error": "ADMIN_BOOTSTRAP_PASSWORD env var not set — cannot run diagnostic"}
    stored_hash = user.password_hash

    try:
        direct_result = _bcrypt.checkpw(test_password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception as e:
        direct_result = f"ERROR: {e}"

    try:
        verify_result = verify_password(test_password, stored_hash)
    except Exception as e:
        verify_result = f"ERROR: {e}"

    new_hash = get_password_hash(test_password)
    rehash_verify = _bcrypt.checkpw(test_password.encode("utf-8"), new_hash.encode("utf-8"))

    return {
        "found": True,
        "email": user.email,
        "hash_prefix": stored_hash[:20],
        "hash_len": len(stored_hash),
        "bcrypt_version": _bcrypt.__version__,
        "direct_verify": direct_result,
        "security_verify": verify_result,
        "rehash_verify": rehash_verify,
        "role_id": str(user.role_id) if user.role_id else None,
        "is_active": user.is_active,
    }

