from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database.db import Base


class Capsule(Base):
    __tablename__ = "capsules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(20), nullable=True)  # image/video/audio/file
    unlock_date = Column(DateTime, nullable=False)
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    is_unlocked = Column(Boolean, default=False)
    is_reviewed = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)   # tracks if unlock email was sent
    report_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", backref="capsules")
