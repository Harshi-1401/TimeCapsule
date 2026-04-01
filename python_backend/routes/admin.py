from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel

from database.db import get_db
from models.user import User, UserRole
from models.room import Room
from models.task import Task
from models.capsule import Capsule
from utils.auth import get_current_user
from routes.capsules import capsule_to_dict

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Stats ──────────────────────────────────────────────────────────────────────
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    total_capsules = db.query(func.count(Capsule.id)).scalar()
    locked = db.query(func.count(Capsule.id)).filter(Capsule.is_unlocked == False).scalar()
    unlocked = db.query(func.count(Capsule.id)).filter(Capsule.is_unlocked == True).scalar()
    reported = db.query(func.count(Capsule.id)).filter(Capsule.report_count > 0).scalar()

    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "bannedUsers": total_users - active_users,
        "totalCapsules": total_capsules,
        "lockedCapsules": locked,
        "unlockedCapsules": unlocked,
        "reportedCapsules": reported,
        "userRegistrations": [],
        "capsuleCreations": [],
    }


# ── User management ────────────────────────────────────────────────────────────
@router.get("/users")
def get_all_users(page: int = 1, limit: int = 10, search: str = "",
                  status: str = "", db: Session = Depends(get_db),
                  _: User = Depends(require_admin)):
    query = db.query(User)
    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "banned":
        query = query.filter(User.is_active == False)

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "users": [
            {
                "_id": str(u.id),
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "isBanned": not u.is_active,
                "createdAt": u.created_at.isoformat(),
                "capsuleCount": db.query(func.count(Capsule.id))
                    .filter(Capsule.user_id == u.id).scalar(),
            }
            for u in users
        ],
        "totalPages": max(1, (total + limit - 1) // limit),
        "total": total,
    }


@router.get("/users/{user_id}")
def get_user_detail(user_id: int, db: Session = Depends(get_db),
                    _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    capsules = db.query(Capsule).filter(Capsule.user_id == user_id).all()
    total = len(capsules)
    locked = sum(1 for c in capsules if not c.is_unlocked)

    return {
        "user": {
            "_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "isBanned": not user.is_active,
            "createdAt": user.created_at.isoformat(),
            "lastLogin": user.created_at.isoformat(),
        },
        "stats": {
            "totalCapsules": total,
            "lockedCapsules": locked,
            "unlockedCapsules": total - locked,
        },
        "capsules": [capsule_to_dict(c) for c in capsules[:10]],
    }


class UserUpdate(BaseModel):
    action: Optional[str] = None   # "ban" | "unban"
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.action == "ban":
        user.is_active = False
    elif payload.action == "unban":
        user.is_active = True
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = payload.role

    db.commit()
    db.refresh(user)
    return {"message": "User updated", "_id": str(user.id)}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


# ── Capsule moderation ─────────────────────────────────────────────────────────
@router.get("/capsules")
def get_all_capsules(page: int = 1, limit: int = 10, filter: str = "",
                     db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(Capsule)
    if filter == "locked":
        query = query.filter(Capsule.is_unlocked == False)
    elif filter == "unlocked":
        query = query.filter(Capsule.is_unlocked == True)
    elif filter == "reported":
        query = query.filter(Capsule.report_count > 0)

    total = query.count()
    capsules = query.offset((page - 1) * limit).limit(limit).all()

    # Enrich with owner info
    result = []
    for c in capsules:
        d = capsule_to_dict(c)
        owner = db.query(User).filter(User.id == c.user_id).first()
        d["userId"] = {
            "name": owner.name if owner else "Unknown",
            "email": owner.email if owner else "N/A",
        }
        result.append(d)

    return {
        "capsules": result,
        "totalPages": max(1, (total + limit - 1) // limit),
        "total": total,
    }


@router.delete("/capsules/{capsule_id}")
def admin_delete_capsule(capsule_id: int, db: Session = Depends(get_db),
                         _: User = Depends(require_admin)):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    db.delete(capsule)
    db.commit()
    return {"message": "Capsule deleted"}


@router.put("/capsules/{capsule_id}/review")
def review_capsule(capsule_id: int, db: Session = Depends(get_db),
                   _: User = Depends(require_admin)):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    capsule.is_reviewed = True
    db.commit()
    return {"message": "Capsule reviewed"}
