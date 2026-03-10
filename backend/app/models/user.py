"""
User Model - Handles authentication and user management
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    
    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    
    # Profile
    phone = Column(String(20))
    avatar_url = Column(String(500))
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Agent-specific fields
    department = Column(String(100))  # For agents
    agent_skills = Column(String(500))  # Comma-separated skills
    max_tickets = Column(Integer, default=10)  # Max concurrent tickets for agents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    last_activity_at = Column(DateTime)
    
    # Relationships
    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    tickets_assigned = relationship("Ticket", back_populates="assigned_agent", foreign_keys="Ticket.assigned_to")
    chat_sessions = relationship("ChatSession", back_populates="user")
    ticket_messages = relationship("TicketMessage", back_populates="sender")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    @property
    def is_agent(self) -> bool:
        """Check if user is an agent or higher"""
        return self.role in [UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
