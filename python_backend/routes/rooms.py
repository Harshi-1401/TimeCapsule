import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from models.user import User
from models.room import Room, RoomMember
from schemas.room import RoomCreate, RoomJoin, RoomResponse, RoomUpdate
from utils.auth import get_current_user

router = APIRouter(prefix="/api/rooms", tags=["Rooms"])


def _generate_invite_code(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _get_room_or_404(room_id: int, db: Session) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


# ── Create a room ──────────────────────────────────────────────────────────────
@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    invite_code = _generate_invite_code()
    room = Room(name=payload.name, description=payload.description,
                invite_code=invite_code, owner_id=current_user.id)
    db.add(room)
    db.flush()  # get room.id before commit

    # Owner is automatically a member
    db.add(RoomMember(room_id=room.id, user_id=current_user.id))
    db.commit()
    db.refresh(room)
    return room


# ── Join a room via invite code ────────────────────────────────────────────────
@router.post("/join", response_model=RoomResponse)
def join_room(payload: RoomJoin, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.invite_code == payload.invite_code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    already_member = db.query(RoomMember).filter(
        RoomMember.room_id == room.id, RoomMember.user_id == current_user.id
    ).first()
    if already_member:
        raise HTTPException(status_code=400, detail="Already a member of this room")

    db.add(RoomMember(room_id=room.id, user_id=current_user.id))
    db.commit()
    db.refresh(room)
    return room


# ── Get all rooms the current user belongs to ─────────────────────────────────
@router.get("/", response_model=List[RoomResponse])
def get_my_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    memberships = db.query(RoomMember).filter(RoomMember.user_id == current_user.id).all()
    room_ids = [m.room_id for m in memberships]
    return db.query(Room).filter(Room.id.in_(room_ids)).all()


# ── Get a single room ──────────────────────────────────────────────────────────
@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    room = _get_room_or_404(room_id, db)
    _assert_member(room_id, current_user.id, db)
    return room


# ── Update room (owner only) ───────────────────────────────────────────────────
@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    room = _get_room_or_404(room_id, db)
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the room owner can update it")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


# ── Delete room (owner only) ───────────────────────────────────────────────────
@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    room = _get_room_or_404(room_id, db)
    if room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the room owner can delete it")
    db.delete(room)
    db.commit()


# ── Leave a room ───────────────────────────────────────────────────────────────
@router.delete("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_room(room_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id, RoomMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="You are not a member of this room")
    db.delete(membership)
    db.commit()


# ── Helper ─────────────────────────────────────────────────────────────────────
def _assert_member(room_id: int, user_id: int, db: Session):
    if not db.query(RoomMember).filter(
        RoomMember.room_id == room_id, RoomMember.user_id == user_id
    ).first():
        raise HTTPException(status_code=403, detail="You are not a member of this room")
