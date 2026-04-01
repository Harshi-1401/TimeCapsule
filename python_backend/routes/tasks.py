from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from models.user import User
from models.room import Room, RoomMember
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from utils.auth import get_current_user

router = APIRouter(prefix="/api/rooms/{room_id}/tasks", tags=["Tasks"])


def _assert_member(room_id: int, user_id: int, db: Session):
    if not db.query(RoomMember).filter(
        RoomMember.room_id == room_id, RoomMember.user_id == user_id
    ).first():
        raise HTTPException(status_code=403, detail="You are not a member of this room")


def _get_task_or_404(task_id: int, room_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.room_id == room_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ── Create task ────────────────────────────────────────────────────────────────
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(room_id: int, payload: TaskCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    _assert_member(room_id, current_user.id, db)

    if not db.query(Room).filter(Room.id == room_id).first():
        raise HTTPException(status_code=404, detail="Room not found")

    task = Task(**payload.model_dump(), room_id=room_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# ── Get all tasks in a room ────────────────────────────────────────────────────
@router.get("/", response_model=List[TaskResponse])
def get_tasks(room_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    _assert_member(room_id, current_user.id, db)
    return db.query(Task).filter(Task.room_id == room_id).all()


# ── Get a single task ──────────────────────────────────────────────────────────
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(room_id: int, task_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    _assert_member(room_id, current_user.id, db)
    return _get_task_or_404(task_id, room_id, db)


# ── Update task ────────────────────────────────────────────────────────────────
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(room_id: int, task_id: int, payload: TaskUpdate,
                db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _assert_member(room_id, current_user.id, db)
    task = _get_task_or_404(task_id, room_id, db)

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


# ── Delete task ────────────────────────────────────────────────────────────────
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(room_id: int, task_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    _assert_member(room_id, current_user.id, db)
    task = _get_task_or_404(task_id, room_id, db)
    db.delete(task)
    db.commit()
