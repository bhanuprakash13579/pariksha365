from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, create_password_reset_token, verify_password_reset_token
)
from app.schemas.auth_schema import Token

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        name=user_in.name,
        phone=user_in.phone,
        role_id=user_in.role_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)

async def forgot_password(db: AsyncSession, email: str) -> str:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        # Return generic message to prevent email enumeration
        return "If an account with this email exists, a password reset token has been generated."
    token = create_password_reset_token(subject=user.id)
    # In production, send this token via email. For now, return it directly.
    return token

async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    try:
        user_id = verify_password_reset_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.password_hash = get_password_hash(new_password)
    await db.commit()

async def update_user(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.phone is not None:
        user.phone = user_update.phone
    await db.commit()
    await db.refresh(user)
    return user

async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    user.password_hash = get_password_hash(new_password)
    await db.commit()
