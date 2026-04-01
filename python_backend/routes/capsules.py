import os
import shutil
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.db import get_db
from models.user import User
from models.capsule import Capsule
from utils.auth import get_current_user

router = APIRouter(prefix="/api/capsules", tags=["Capsules"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def capsule_to_dict(c: Capsule) -> dict:
    """Convert Capsule ORM object to a dict. Returns relative mediaUrl path."""
    return {
        "_id": str(c.id),
        "id": c.id,
        "title": c.title,
        "message": c.message,
        "mediaUrl": c.media_url,  # relative path e.g. /uploads/1_123456.jpg
        "mediaType": c.media_type,
        "unlockDate": c.unlock_date.isoformat() if c.unlock_date else None,
        "isPublic": c.is_public,
        "isEncrypted": c.is_encrypted,
        "isUnlocked": c.is_unlocked,
        "isReviewed": c.is_reviewed,
        "reportCount": c.report_count,
        "userId": c.user_id,
        "createdAt": c.created_at.isoformat() if c.created_at else None,
    }


def _auto_unlock(capsule: Capsule):
    """Mark capsule as unlocked if its unlock date has passed.
    Always compare as naive datetimes to avoid tz offset issues
    when the frontend sends local time with no timezone info.
    """
    if not capsule.is_unlocked:
        unlock_dt = capsule.unlock_date
        # Strip timezone info so comparison is always naive local time
        if unlock_dt.tzinfo is not None:
            unlock_dt = unlock_dt.replace(tzinfo=None)
        if datetime.now() >= unlock_dt:
            capsule.is_unlocked = True


# ── Public capsules (no auth) ──────────────────────────────────────────────────
@router.get("/public")
def get_public_capsules(db: Session = Depends(get_db)):
    capsules = db.query(Capsule).filter(Capsule.is_public == True).all()
    for c in capsules:
        _auto_unlock(c)
    db.commit()
    return [capsule_to_dict(c) for c in capsules if c.is_unlocked]


# ── Create capsule ─────────────────────────────────────────────────────────────
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_capsule(
    title: str = Form(...),
    message: str = Form(""),
    unlockDate: str = Form(...),
    isPublic: str = Form("false"),
    isEncrypted: str = Form("false"),
    media: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Parse and strip timezone — store as naive local datetime for consistent comparison
    unlock_dt = datetime.fromisoformat(unlockDate.replace("Z", ""))
    unlock_dt = unlock_dt.replace(tzinfo=None)

    media_url = None
    media_type = None
    if media and media.filename:
        ext = os.path.splitext(media.filename)[1].lower()
        filename = f"{current_user.id}_{int(datetime.now().timestamp())}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(media.file, f)
        media_url = f"/uploads/{filename}"

        if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            media_type = "image"
        elif ext in [".mp4", ".mov", ".avi", ".webm"]:
            media_type = "video"
        elif ext in [".mp3", ".wav", ".ogg", ".m4a"]:
            media_type = "audio"
        else:
            media_type = "file"

    capsule = Capsule(
        title=title,
        message=message,
        unlock_date=unlock_dt,
        is_public=isPublic.lower() == "true",
        is_encrypted=isEncrypted.lower() == "true",
        media_url=media_url,
        media_type=media_type,
        user_id=current_user.id,
    )
    db.add(capsule)
    db.commit()
    db.refresh(capsule)
    return capsule_to_dict(capsule)


# ── Get all capsules for current user ──────────────────────────────────────────
@router.get("/")
def get_capsules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    capsules = db.query(Capsule).filter(Capsule.user_id == current_user.id).all()
    for c in capsules:
        _auto_unlock(c)
    db.commit()
    return [capsule_to_dict(c) for c in capsules]


# ── Get single capsule ─────────────────────────────────────────────────────────
@router.get("/{capsule_id}")
def get_capsule(capsule_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id, Capsule.user_id == current_user.id
    ).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    _auto_unlock(capsule)
    db.commit()
    return capsule_to_dict(capsule)


# ── Delete capsule ─────────────────────────────────────────────────────────────
@router.delete("/{capsule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_capsule(capsule_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id, Capsule.user_id == current_user.id
    ).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    # Remove uploaded file if exists
    if capsule.media_url:
        filepath = capsule.media_url.lstrip("/")
        if os.path.exists(filepath):
            os.remove(filepath)
    db.delete(capsule)
    db.commit()


# ── Report capsule ─────────────────────────────────────────────────────────────
class ReportPayload(BaseModel):
    reason: str

@router.post("/{capsule_id}/report")
def report_capsule(capsule_id: int, payload: ReportPayload,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    capsule.report_count += 1
    db.commit()
    return {"message": "Capsule reported"}
