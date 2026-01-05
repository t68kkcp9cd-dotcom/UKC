"""
Authentication endpoints
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.database import get_db
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.config import settings
from app.utils.security import create_access_token, create_refresh_token, verify_password
from app.services.audit_service import AuditService

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
logger = logging.getLogger(__name__)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    result = await db.execute(
        select(User).where(
            (User.username == username) | (User.email == username),
            User.is_active == True
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends(AuditService)
):
    """Register a new user"""
    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password
    password_hash = pwd_context.hash(user_data.password)
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        household_id=user_data.household_id
    )
    
    db.add(user)
    await db.flush()
    
    # Create household if not joining existing one
    if not user_data.household_id:
        from app.models.user import Household
        household = Household(name=f"{user_data.username}'s Household", owner_id=user.id)
        db.add(household)
        await db.flush()
        user.household_id = household.id
    
    await db.commit()
    await db.refresh(user)
    
    # Log registration
    await audit_service.log_action(
        user.id, "CREATE", "user", user.id,
        new_values={"username": user.username, "email": user.email}
    )
    
    logger.info(f"User registered: {user.username}")
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get JWT token"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    )
    
    # Store session
    session = UserSession(
        user_id=user.id,
        token_hash=hashlib.sha256(access_token.encode()).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    db.add(session)
    await db.commit()
    
    logger.info(f"User logged in: {user.username}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Logout and invalidate token"""
    # Delete session
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    await db.execute(
        delete(UserSession).where(UserSession.token_hash == token_hash)
    )
    await db.commit()
    
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user