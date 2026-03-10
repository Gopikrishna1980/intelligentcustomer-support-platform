"""
Base models import - Used by Alembic for migrations
"""
from app.core.database import Base

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.ticket import Ticket, TicketMessage, TicketTag
from app.models.chat import ChatSession, ChatMessage
from app.models.kb import KnowledgeArticle, KnowledgeCategory
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "User",
    "Ticket",
    "TicketMessage", 
    "TicketTag",
    "ChatSession",
    "ChatMessage",
    "KnowledgeArticle",
    "KnowledgeCategory",
    "AuditLog"
]
