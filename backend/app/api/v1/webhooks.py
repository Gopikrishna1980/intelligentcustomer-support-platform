"""
Webhooks API endpoints for integrations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from app.core.database import get_db
from app.api.dependencies import get_current_agent
from app.models.user import User
from app.schemas.common import SuccessResponse
from pydantic import BaseModel

router = APIRouter()


class WebhookSubscription(BaseModel):
    """Webhook subscription schema"""
    url: str
    events: list[str]
    secret: str


@router.post("/slack/events")
async def slack_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive Slack events
    
    TODO: Implement Slack integration
    - Ticket notifications to Slack channels
    - Create tickets from Slack messages
    - Agent status updates
    """
    body = await request.json()
    
    # Slack URL verification challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}
    
    # Handle events
    event = body.get("event", {})
    event_type = event.get("type")
    
    if event_type == "message":
        # Handle Slack message (could create ticket)
        pass
    
    return {"ok": True}


@router.post("/jira/issues")
async def jira_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive Jira issue events
    
    TODO: Implement Jira integration
    - Sync tickets with Jira issues
    - Update ticket status from Jira
    - Create Jira issues from critical tickets
    """
    body = await request.json()
    
    webhook_event = body.get("webhookEvent")
    issue = body.get("issue", {})
    
    if webhook_event == "jira:issue_created":
        # Handle new Jira issue
        pass
    elif webhook_event == "jira:issue_updated":
        # Handle Jira issue update
        pass
    
    return {"status": "received"}


@router.get("/subscriptions")
async def list_webhook_subscriptions(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    List webhook subscriptions
    
    TODO: Implement webhook subscription storage
    """
    return {
        "subscriptions": [
            {
                "id": "1",
                "service": "slack",
                "url": "https://hooks.slack.com/services/...",
                "events": ["ticket.created", "ticket.closed"],
                "active": True
            }
        ]
    }


@router.post("/subscriptions")
async def create_webhook_subscription(
    subscription: WebhookSubscription,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Create webhook subscription
    
    TODO: Implement webhook subscription
    """
    return SuccessResponse(
        message="Webhook subscription created",
        data={"id": "new-webhook-id"}
    )


@router.delete("/subscriptions/{subscription_id}")
async def delete_webhook_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Delete webhook subscription
    """
    return SuccessResponse(message="Webhook subscription deleted")


@router.post("/test")
async def test_webhook(
    url: str,
    current_user: User = Depends(get_current_agent)
):
    """
    Test webhook URL
    """
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"event": "test", "message": "Test webhook from support platform"},
                timeout=5.0
            )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text[:200]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
