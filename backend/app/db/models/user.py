import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username       = Column(String(32), unique=True, nullable=False, index=True)
    email          = Column(String(255), unique=True, nullable=False, index=True)
    password_hash  = Column(String(255), nullable=False)
    display_name   = Column(String(64), nullable=True)
    bio            = Column(Text, default="")
    profile_picture= Column(String(512), nullable=True)
    is_active      = Column(Boolean, default=True)
    is_verified    = Column(Boolean, default=True)   # MVP: auto-verified
    is_admin       = Column(Boolean, default=False)
    online         = Column(Boolean, default=False)
    last_seen      = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at     = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at     = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    messages        = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    chat_memberships= relationship("ChatMember", back_populates="user", cascade="all, delete-orphan")
