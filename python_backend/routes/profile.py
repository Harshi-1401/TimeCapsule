from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from schemas.user import UserResponse, ProfileUpdate
from utils.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Return the currently logged-in user's profile."""
    return current_user


@router.put("/", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update name, email, and/or profile_image for the logged-in user."""

    # Check email uniqueness if the user wants to change it
    if payload.email and payload.email != current_user.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another account",
            )
        current_user.email = payload.email

    if payload.name is not None:
        current_user.name = payload.name

    if payload.profile_image is not None:
        current_user.profile_image = payload.profile_image

    db.commit()
    db.refresh(current_user)
    return current_user
