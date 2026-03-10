"""
Chat Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ChatSessionCreate(BaseModel):
    """Schema for starting a new chat session"""
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None
    initial_message: Optional[str] = None


class ChatMessageCreate(BaseModel):
    """Schema for sending a chat message"""
    content: str = Field(..., min_length=1, max_length=5000)
    attachments: Optional[List[str]] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: UUID
    session_id: UUID
    sender_id: Optional[UUID]
    sender_name: str
    sender_type: str  # customer, agent, bot
    content: str
    is_ai_generated: bool
    ai_confidence: Optional[float]
    ai_sentiment: Optional[str]
    attachments: Optional[str]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: UUID
    session_id: str
    user_id: UUID
    agent_id: Optional[UUID]
    agent_name: Optional[str]
    is_active: bool
    is_bot_only: bool
    
    # Metadata
    user_ip: Optional[str]
    user_agent: Optional[str]
    page_url: Optional[str]
    
    # AI analysis
    ai_sentiment: Optional[str]
    ai_topic: Optional[str]
    ai_intent: Optional[str]
    
    # Metrics
    message_count: int
    bot_message_count: int
    agent_message_count: int
    satisfaction_score: Optional[int]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]
    agent_joined_at: Optional[datetime]
    
    # Messages (optional, loaded separately)
    messages: Optional[List[ChatMessageResponse]] = None
    
    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Schema for chat session list (simplified)"""
    id: UUID
    session_id: str
    user_id: UUID
    user_name: str
    agent_id: Optional[UUID]
    agent_name: Optional[str]
    is_active: bool
    is_bot_only: bool
    ai_sentiment: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionUpdate(BaseModel):
    """Schema for updating chat session"""
    agent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5)


class ChatSessionEnd(BaseModel):
    """Schema for ending chat session"""
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5, description="1-5 rating")
    feedback: Optional[str] = None


class ChatTypingIndicator(BaseModel):
    """Schema for typing indicator"""
    session_id: str
    user_id: UUID
    is_typing: bool


class ChatAgentJoin(BaseModel):
    """Schema for agent joining chat"""
    session_id: UUID
    agent_id: UUID


class ChatTranscriptRequest(BaseModel):
    """Schema for requesting chat transcript"""
    session_id: UUID
    format: str = Field("json", pattern="^(json|text|pdf)$")


class ChatStats(BaseModel):
    """Schema for chat statistics"""
    total_sessions: int
    active_sessions: int
    bot_only_sessions: int
    with_agent_sessions: int
    avg_messages_per_session: float
    avg_session_duration_minutes: Optional[float]
    avg_satisfaction_score: Optional[float]
    total_messages: int


class ChatFilterParams(BaseModel):
    """Schema for filtering chat sessions"""
    user_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    is_bot_only: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_satisfaction: Optional[int] = Field(None, ge=1, le=5)
