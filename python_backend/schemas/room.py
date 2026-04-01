from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from schemas.user import UserResponse


class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoomJoin(BaseModel):
    invite_code: str


class MemberResponse(BaseModel):
    id: int
    user: UserResponse
    joined_at: datetime

    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    is_active: bool
    owner_id: int
    created_at: datetime
    members: List[MemberResponse] = []

    model_config = {"from_attributes": True}


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
