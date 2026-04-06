import os
import base64
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.db import get_db
from models.user import User
from models.capsule import Capsule
from utils.auth import get_current_user

router = APIRouter(prefix="/api/capsules", tags=["Capsules"])

# Max file size: 5MB (base64 stored in DB)
MAX_FILE_BYTES = 5 * 1024 * 1024


# ── Helpers ────────────────────────────────────────────────────────────────────
def capsule_to_dict(c: Capsule) -> dict:
    # Handle both old file-path URLs and new base64 data URIs
    media_url = c.media_url
    if media_url and media_url.startswith("/uploads/"):
        # Old format — file no longer exists on Render, return None
        media_url = None

    return {
        "_id": str(c.id),
        "id": c.id,
        "title": c.title,
        "message": c.message,
        "mediaUrl": media_url,
        "mediaType": c.media_type if media_url else None,
        "mediaFilename": c.media_filename,
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
    """Unlock capsule if unlock_date has passed. All datetimes in UTC."""
    if capsule.is_unlocked:
        return
    now_utc = datetime.now(timezone.utc)
    unlock_dt = capsule.unlock_date
    # Ensure unlock_dt is timezone-aware UTC
    if unlock_dt.tzinfo is None:
        unlock_dt = unlock_dt.replace(tzinfo=timezone.utc)
    if now_utc >= unlock_dt:
        capsule.is_unlocked = True


def _detect_media_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "image"
    elif ext in [".mp4", ".mov", ".avi", ".webm"]:
        return "video"
    elif ext in [".mp3", ".wav", ".ogg", ".m4a"]:
        return "audio"
    return "file"


def _mime_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp",
        ".mp4": "video/mp4", ".mov": "video/quicktime",
        ".avi": "video/x-msvideo", ".webm": "video/webm",
        ".mp3": "audio/mpeg", ".wav": "audio/wav",
        ".ogg": "audio/ogg", ".m4a": "audio/mp4",
        ".pdf": "application/pdf",
    }
    return mime_map.get(ext, "application/octet-stream")


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
    # Parse unlock date — frontend sends ISO string (local or UTC)
    # Normalize to UTC-aware datetime
    raw = unlockDate.replace("Z", "+00:00")
    try:
        unlock_dt = datetime.fromisoformat(raw)
    except ValueError:
        unlock_dt = datetime.fromisoformat(unlockDate.replace("Z", ""))
        unlock_dt = unlock_dt.replace(tzinfo=timezone.utc)

    if unlock_dt.tzinfo is None:
        unlock_dt = unlock_dt.replace(tzinfo=timezone.utc)

    media_url = None
    media_type = None
    media_filename = None

    if media and media.filename:
        file_bytes = await media.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 5MB."
            )
        media_type = _detect_media_type(media.filename)
        mime = _mime_type(media.filename)
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        media_url = f"data:{mime};base64,{b64}"   # self-contained data URI
        media_filename = media.filename

    capsule = Capsule(
        title=title,
        message=message,
        unlock_date=unlock_dt,
        is_public=isPublic.lower() == "true",
        is_encrypted=isEncrypted.lower() == "true",
        media_url=media_url,
        media_type=media_type,
        media_filename=media_filename,
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
