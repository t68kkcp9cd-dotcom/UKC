"""
User management endpoints
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, UserProfile, Household
from app.schemas.user import (
    UserResponse, UserUpdate, UserProfileResponse, UserProfileUpdate,
    HouseholdCreate, HouseholdResponse, HouseholdUpdate
)
from app.services.audit_service import AuditService
from app.api.v1.auth import get_current_user
from app.utils.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information with profile"""
    # Refresh user data with relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile), selectinload(User.household))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update current user information"""
    # Store old values for audit
    old_values = {
        "username": current_user.username,
        "email": current_user.email
    }
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password":
            # Hash password if provided
            current_user.password_hash = get_password_hash(value)
        else:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "user", current_user.id,
        old_values=old_values,
        new_values=update_data
    )
    
    return current_user


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Create default profile if it doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    
    return profile


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update current user's profile"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "user_profile", profile.id,
        new_values=update_data
    )
    
    return profile


@router.get("/household", response_model=Optional[HouseholdResponse])
async def get_user_household(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's household"""
    if not current_user.household_id:
        return None
    
    result = await db.execute(
        select(Household)
        .options(selectinload(Household.users))
        .where(Household.id == current_user.household_id)
    )
    household = result.scalar_one_or_none()
    
    return household


@router.post("/household", response_model=HouseholdResponse)
async def create_household(
    household_data: HouseholdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new household"""
    # Check if user already owns a household
    if current_user.owned_household:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already owns a household"
        )
    
    # Create household
    household = Household(
        name=household_data.name,
        owner_id=current_user.id
    )
    
    db.add(household)
    await db.flush()
    
    # Add user to household
    current_user.household_id = household.id
    await db.commit()
    await db.refresh(household)
    
    # Load users
    await db.execute(
        select(Household)
        .options(selectinload(Household.users))
        .where(Household.id == household.id)
    )
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "household", household.id,
        new_values={"name": household.name}
    )
    
    return household


@router.put("/household", response_model=HouseholdResponse)
async def update_household(
    household_update: HouseholdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update current user's household"""
    if not current_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of a household"
        )
    
    # Only household owner can update
    if not current_user.owned_household:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household owner can update household"
        )
    
    household = current_user.owned_household
    
    # Store old values for audit
    old_values = {"name": household.name}
    
    # Update fields
    update_data = household_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(household, field, value)
    
    await db.commit()
    await db.refresh(household)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "household", household.id,
        old_values=old_values,
        new_values=update_data
    )
    
    return household


@router.post("/household/invite", response_model=Dict[str, Any])
async def invite_to_household(
    email: str = Query(..., description="Email of user to invite"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Invite a user to join the household"""
    if not current_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of a household"
        )
    
    if not current_user.owned_household:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household owner can invite users"
        )
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    invited_user = result.scalar_one_or_none()
    
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    
    if invited_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already part of a household"
        )
    
    # Generate invitation token (simplified)
    invitation_token = f"invite_{current_user.household_id}_{invited_user.id}"
    
    # Log invitation
    await audit_service.log_action(
        current_user.id, "INVITE", "household", current_user.household_id,
        new_values={
            "invited_user_id": str(invited_user.id),
            "invited_email": email,
            "invitation_token": invitation_token
        }
    )
    
    return {
        "message": f"Invitation sent to {email}",
        "invitation_token": invitation_token,
        "household_name": current_user.owned_household.name
    }


@router.post("/household/join", response_model=HouseholdResponse)
async def join_household(
    invitation_token: str = Query(..., description="Household invitation token"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Join a household using invitation token"""
    # Validate invitation token (simplified)
    try:
        parts = invitation_token.split("_")
        if len(parts) != 3 or parts[0] != "invite":
            raise ValueError("Invalid token format")
            
        household_id = parts[1]
        invited_user_id = parts[2]
        
        if str(current_user.id) != invited_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invitation token is for a different user"
            )
            
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invitation token"
        )
    
    # Check if user is already in a household
    if current_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already part of a household"
        )
    
    # Get household
    result = await db.execute(
        select(Household).where(Household.id == UUID(household_id))
    )
    household = result.scalar_one_or_none()
    
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    
    # Join household
    current_user.household_id = household.id
    await db.commit()
    await db.refresh(household)
    
    # Load users
    await db.execute(
        select(Household)
        .options(selectinload(Household.users))
        .where(Household.id == household.id)
    )
    
    # Log action
    await audit_service.log_action(
        current_user.id, "JOIN", "household", household.id,
        new_values={"household_name": household.name}
    )
    
    return household


@router.post("/household/leave", response_model=Dict[str, str])
async def leave_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Leave current household"""
    if not current_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of a household"
        )
    
    # Check if user is the owner
    if current_user.owned_household:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Household owner cannot leave. Transfer ownership first."
        )
    
    household_id = current_user.household_id
    household_name = current_user.household.name if current_user.household else "Unknown"
    
    # Leave household
    current_user.household_id = None
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "LEAVE", "household", household_id,
        old_values={"household_name": household_name}
    )
    
    return {"message": f"Left household: {household_name}"}


@router.post("/avatar", response_model=Dict[str, str])
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Upload user avatar"""
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # In production, this would upload to S3 or similar
    # For now, just return a mock URL
    avatar_url = f"https://example.com/avatars/{current_user.id}.jpg"
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "user_avatar", current_user.id,
        new_values={"avatar_url": avatar_url}
    )
    
    return {"avatar_url": avatar_url}


@router.get("/activity", response_model=Dict[str, Any])
async def get_user_activity(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Get user's activity summary"""
    activity_summary = await audit_service.get_user_activity_summary(
        db=db,
        user_id=str(current_user.id),
        days=days
    )
    
    return activity_summary


@router.get("/household/members", response_model=List[UserResponse])
async def get_household_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of the current user's household"""
    if not current_user.household_id:
        return []
    
    result = await db.execute(
        select(User)
        .where(
            User.household_id == current_user.household_id,
            User.is_active == True
        )
        .order_by(User.created_at)
    )
    
    members = result.scalars().all()
    return members