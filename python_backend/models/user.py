from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from database.db import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(Boolean, default=True)
    profile_image = Column(String(500), nullable=True)  # URL or file path
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    owned_rooms = relationship("Room", back_populates="owner", cascade="all, delete-orphan")
    memberships = relationship("RoomMember", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assigned_user", cascade="all, delete-orphan")
