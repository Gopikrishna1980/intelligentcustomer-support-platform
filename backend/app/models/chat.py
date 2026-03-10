"""
Chat Models - Real-time chat sessions and messages
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Participants
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Session info
    is_active = Column(Boolean, default=True)
    is_bot_only = Column(Boolean, default=True)  # True until agent joins
    
    # Metadata
    user_ip = Column(String(45))
    user_agent = Column(String(500))
    page_url = Column(String(500))
    
    # AI analysis
    ai_sentiment = Column(String(20))  # Overall session sentiment
    ai_topic = Column(String(100))  # Detected topic
    ai_intent = Column(String(50))
    
    # Metrics
    message_count = Column(Integer, default=0)
    bot_message_count = Column(Integer, default=0)
    agent_message_count = Column(Integer, default=0)
    satisfaction_score = Column(Integer)  # 1-5
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime)
    agent_joined_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions", foreign_keys=[user_id])
    agent = relationship("User", foreign_keys=[agent_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.session_id}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message info
    content = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'customer', 'agent', 'bot'
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # AI features
    is_ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Integer)  # 0-100
    ai_sentiment = Column(String(20))
    
    # Metadata
    is_read = Column(Boolean, default=False)
    attachments = Column(Text)  # JSON array of attachment URLs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    
    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.sender_type}>"
