"""
Ticket Models - Support ticket management
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TicketStatus(str, enum.Enum):
    """Ticket statuses"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_AGENT = "waiting_agent"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Ticket priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    """Ticket categories"""
    TECHNICAL = "technical"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"
    COMPLAINT = "complaint"


# Many-to-many relationship between tickets and tags
ticket_tags_association = Table(
    'ticket_tags_association',
    Base.metadata,
    Column('ticket_id', UUID(as_uuid=True), ForeignKey('tickets.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('ticket_tags.id'), primary_key=True)
)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "TKT-001234"
    
    # Basic info
    subject = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Status and priority
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    category = Column(SQLEnum(TicketCategory), default=TicketCategory.GENERAL)
    
    # AI-generated fields
    ai_sentiment = Column(String(20))  # positive, negative, neutral
    ai_intent = Column(String(50))  # refund, help, complaint, etc.
    ai_suggested_category = Column(String(50))
    ai_tags = Column(String(500))  # Comma-separated AI-generated tags
    
    # Relationships (Foreign Keys)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # SLA tracking
    sla_due_date = Column(DateTime)
    first_response_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Metrics
    response_count = Column(Integer, default=0)
    customer_satisfaction_score = Column(Integer)  # 1-5
    resolution_time_minutes = Column(Integer)
    
    # Flags
    is_escalated = Column(Boolean, default=False)
    is_merged = Column(Boolean, default=False)
    merged_into_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="tickets_created", foreign_keys=[creator_id])
    assigned_agent = relationship("User", back_populates="tickets_assigned", foreign_keys=[assigned_to])
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    tags = relationship("TicketTag", secondary=ticket_tags_association, back_populates="tickets")
    merged_tickets = relationship("Ticket", remote_side=[id])
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number} - {self.status}>"


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to customer
    
    # AI features
    ai_suggested = Column(Boolean, default=False)  # Was this AI-suggested?
    ai_sentiment = Column(String(20))
    
    # Attachments
    attachments = Column(Text)  # JSON array of attachment URLs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    read_at = Column(DateTime)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    sender = relationship("User", back_populates="ticket_messages")
    
    def __repr__(self):
        return f"<TicketMessage {self.id} for Ticket {self.ticket_id}>"


class TicketTag(Base):
    __tablename__ = "ticket_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#3B82F6")  # Hex color code
    description = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", secondary=ticket_tags_association, back_populates="tags")
    
    def __repr__(self):
        return f"<TicketTag {self.name}>"
