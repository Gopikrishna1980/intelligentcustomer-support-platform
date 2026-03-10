"""
API v1 router aggregation
"""
from fastapi import APIRouter

from app.api.v1 import auth, tickets, chat, analytics, kb, webhooks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(kb.router, prefix="/kb", tags=["Knowledge Base"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

__all__ = ["api_router"]
