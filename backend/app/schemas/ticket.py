"""
Ticket Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.ticket import TicketStatus, TicketPriority, TicketCategory


class TicketBase(BaseModel):
    """Base ticket schema"""
    subject: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    """Schema for creating a ticket"""
    pass


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    subject: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to: Optional[UUID] = None


class TicketAssign(BaseModel):
    """Schema for assigning ticket to agent"""
    agent_id: UUID


class TicketClose(BaseModel):
    """Schema for closing a ticket"""
    resolution_notes: Optional[str] = None
    customer_satisfaction_score: Optional[int] = Field(None, ge=1, le=5)


class TicketMerge(BaseModel):
    """Schema for merging tickets"""
    merge_into_id: UUID
    merge_reason: Optional[str] = None


class TicketMessageCreate(BaseModel):
    """Schema for creating a ticket message"""
    content: str = Field(..., min_length=1)
    is_internal: bool = Field(False, description="Internal note (hidden from customer)")
    attachments: Optional[List[str]] = None


class TicketMessageResponse(BaseModel):
    """Schema for ticket message response"""
    id: UUID
    ticket_id: UUID
    sender_id: UUID
    sender_name: str
    sender_role: str
    content: str
    is_internal: bool
    ai_suggested: bool
    ai_sentiment: Optional[str]
    attachments: Optional[str]
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TicketTagCreate(BaseModel):
    """Schema for creating a ticket tag"""
    name: str = Field(..., min_length=2, max_length=50)
    color: str = Field("#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None


class TicketTagResponse(BaseModel):
    """Schema for ticket tag response"""
    id: UUID
    name: str
    color: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Schema for detailed ticket response"""
    id: UUID
    ticket_number: str
    subject: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    
    # AI fields
    ai_sentiment: Optional[str]
    ai_intent: Optional[str]
    ai_suggested_category: Optional[str]
    ai_tags: Optional[str]
    
    # Relationships
    creator_id: UUID
    creator_name: str
    assigned_to: Optional[UUID]
    assigned_agent_name: Optional[str]
    
    # SLA
    sla_due_date: Optional[datetime]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    # Metrics
    response_count: int
    customer_satisfaction_score: Optional[int]
    resolution_time_minutes: Optional[int]
    
    # Flags
    is_escalated: bool
    is_merged: bool
    merged_into_id: Optional[UUID]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Messages and tags (optional, loaded separately)
    messages: Optional[List[TicketMessageResponse]] = None
    tags: Optional[List[TicketTagResponse]] = None
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Schema for ticket list (simplified)"""
    id: UUID
    ticket_number: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    creator_name: str
    assigned_agent_name: Optional[str]
    ai_sentiment: Optional[str]
    response_count: int
    sla_due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TicketFilterParams(BaseModel):
    """Schema for filtering tickets"""
    status: Optional[List[TicketStatus]] = None
    priority: Optional[List[TicketPriority]] = None
    category: Optional[List[TicketCategory]] = None
    assigned_to: Optional[UUID] = None
    creator_id: Optional[UUID] = None
    is_escalated: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None


class TicketStats(BaseModel):
    """Schema for ticket statistics"""
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    avg_response_time_minutes: Optional[float]
    avg_resolution_time_minutes: Optional[float]
    avg_satisfaction_score: Optional[float]
