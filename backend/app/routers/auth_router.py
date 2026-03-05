from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth_schema import Token, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse, GoogleLoginRequest
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
    """
    Login or create a user via Google ID Token.
    """
    return await auth_service.authenticate_google_user(db, token=login_data.token)

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

# TEMPORARY DEBUG - REMOVE AFTER FIXING LOGIN
@router.get("/debug-verify/{email}")
async def debug_verify(email: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from app.models.user import User
    from app.core.security import verify_password, get_password_hash
    import bcrypt as _bcrypt
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        return {"found": False, "email": email}
    
    test_password = "Admin@Parisksha365"
    stored_hash = user.password_hash
    
    # Test 1: Direct bcrypt
    try:
        direct_result = _bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception as e:
        direct_result = f"ERROR: {e}"
    
    # Test 2: via security.verify_password
    try:
        verify_result = verify_password(test_password, stored_hash)
    except Exception as e:
        verify_result = f"ERROR: {e}"
    
    # Test 3: generate a new hash and verify
    new_hash = get_password_hash(test_password)
    rehash_verify = _bcrypt.checkpw(test_password.encode('utf-8'), new_hash.encode('utf-8'))
    
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

