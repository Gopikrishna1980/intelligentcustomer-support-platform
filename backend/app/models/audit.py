"""
Audit Log Model - Track all system activities for compliance
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User who performed the action
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., 'user.login', 'ticket.create'
    resource_type = Column(String(50), nullable=False)  # e.g., 'user', 'ticket', 'chat'
    resource_id = Column(String(100))  # ID of the affected resource
    
    # Details
    description = Column(Text)
    changes = Column(JSONB)  # JSON object showing what changed (before/after)
    metadata = Column(JSONB)  # Additional metadata
    
    # Request info
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_method = Column(String(10))  # GET, POST, etc.
    request_path = Column(String(500))
    
    # Status
    status = Column(String(20), default="success")  # success, failure
    error_message = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
