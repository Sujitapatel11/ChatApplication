import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id              = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id            = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content              = Column(Text, nullable=True)
    message_type         = Column(String(32), default="text")
    deleted_for_everyone = Column(Boolean, default=False)
    replied_to_id        = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    created_at           = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at           = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    chat       = relationship("Chat", back_populates="messages")
    sender     = relationship("User", back_populates="messages")
    replied_to = relationship("Message", remote_side=[id], foreign_keys=[replied_to_id])
