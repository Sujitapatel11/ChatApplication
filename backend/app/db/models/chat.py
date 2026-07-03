import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_group   = Column(Boolean, default=False)
    name       = Column(String(128), nullable=True)  # group name
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    members  = relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat",
                            cascade="all, delete-orphan", order_by="Message.created_at")
