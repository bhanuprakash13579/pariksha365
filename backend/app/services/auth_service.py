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
from app.services import oauth_service
import secrets

async def authenticate_apple_user(db: AsyncSession, identity_token: str, full_name: str | None = None) -> Token:
    payload = await oauth_service.verify_apple_token(identity_token)

    # Apple uses `sub` as the stable user identifier, email may be absent on
    # subsequent logins. We look up by email when present, else by apple_sub.
    email = payload.get("email")
    apple_sub = payload.get("sub", "")

    stmt = select(User).where(User.email == email) if email else select(User).where(User.apple_sub == apple_sub)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        # If email absent (subsequent logins) and no existing user, refuse —
        # we can't create an account without an email.
        if not email:
            raise HTTPException(status_code=400, detail="Apple token missing email. Please sign out of Apple ID on your device and try again.")
        random_password = secrets.token_urlsafe(32)
        derived_name = full_name or (email.split("@")[0] if email else "User")
        user = User(
            email=email,
            password_hash=get_password_hash(random_password),
            name=derived_name,
        )
        # Store apple_sub if the column exists (safe — no-op if column missing)
        try:
            user.apple_sub = apple_sub
        except AttributeError:
            pass
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


async def authenticate_google_user(db: AsyncSession, token: str) -> Token:
    # verify_google_token calls google-auth's sync HTTP client to fetch Google's
    # public certs. Running it in a thread avoids blocking the event loop for
    # the full network round-trip (~50-300 ms), which would otherwise stall every
    # other in-flight request — including Railway's /health check — and could
    # cause spurious 502s with missing CORS headers on concurrent requests.
    import asyncio
    idinfo = await asyncio.to_thread(oauth_service.verify_google_token, token)
    email = idinfo.get("email")
    name = idinfo.get("name")
    
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email")
        
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        # Create a new user with a random password
        random_password = secrets.token_urlsafe(32)
        db_user = User(
            email=email,
            password_hash=get_password_hash(random_password),
            name=name or email.split("@")[0],
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        user = db_user
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)

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
