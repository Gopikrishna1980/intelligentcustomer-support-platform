"""
Ticket Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_agent
from app.models.user import User
from app.models.ticket import Ticket, TicketMessage, TicketTag, TicketStatus, TicketPriority
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketClose,
    TicketMerge,
    TicketMessageCreate,
    TicketResponse,
    TicketListResponse,
    TicketMessageResponse,
    TicketStats
)
from app.schemas.common import SuccessResponse, PaginationParams
from app.services.ai_service import ai_service
from app.services.sentiment_service import sentiment_service
from app.services.routing_service import routing_service

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket
    
    - Analyzes sentiment and intent using AI
    - Auto-categorizes if not provided
    - Assigns to best available agent
    - Sets SLA due date based on priority
    """
    # AI analysis
    sentiment_analysis = sentiment_service.analyze_sentiment(ticket_data.description)
    ai_intent = await ai_service.extract_intent(ticket_data.description)
    
    # Auto-categorize if not provided
    if not ticket_data.category:
        categorization = await ai_service.categorize_ticket(
            ticket_data.subject,
            ticket_data.description
        )
        category = categorization.get("category", "general")
    else:
        category = ticket_data.category
    
    # Generate ticket number
    last_ticket = db.query(Ticket).order_by(Ticket.created_at.desc()).first()
    if last_ticket and last_ticket.ticket_number:
        last_num = int(last_ticket.ticket_number.split('-')[1])
        ticket_number = f"TKT-{str(last_num + 1).zfill(6)}"
    else:
        ticket_number = "TKT-000001"
    
    # Calculate SLA due date based on priority
    priority = ticket_data.priority or TicketPriority.medium
    sla_hours = {
        TicketPriority.urgent: 4,
        TicketPriority.high: 24,
        TicketPriority.medium: 72,
        TicketPriority.low: 168
    }
    sla_due_date = datetime.utcnow() + timedelta(hours=sla_hours[priority])
    
    # Create ticket
    new_ticket = Ticket(
        ticket_number=ticket_number,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status=TicketStatus.open,
        priority=priority,
        category=category,
        creator_id=current_user.id,
        ai_sentiment=sentiment_analysis['sentiment'],
        ai_intent=ai_intent,
        ai_suggested_category=category,
        sla_due_date=sla_due_date
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    # Auto-assign to agent
    assigned_agent_id = await routing_service.assign_best_agent(db, str(new_ticket.id), new_ticket)
    if assigned_agent_id:
        new_ticket.assigned_to = assigned_agent_id
        db.commit()
    
    # Prepare response
    response_data = {
        **new_ticket.__dict__,
        "creator_name": current_user.full_name,
        "assigned_agent_name": None
    }
    
    if new_ticket.assigned_to:
        agent = db.query(User).filter(User.id == new_ticket.assigned_to).first()
        if agent:
            response_data["assigned_agent_name"] = agent.full_name
    
    return response_data


@router.get("", response_model=List[TicketListResponse])
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    assigned_to_me: bool = False,
    created_by_me: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List tickets with filters and pagination
    """
    query = db.query(Ticket)
    
    # Filters
    if status:
        query = query.filter(Ticket.status == status)
    
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    if assigned_to_me:
        query = query.filter(Ticket.assigned_to == current_user.id)
    
    if created_by_me:
        query = query.filter(Ticket.creator_id == current_user.id)
    
    if search:
        query = query.filter(
            or_(
                Ticket.subject.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%"),
                Ticket.ticket_number.ilike(f"%{search}%")
            )
        )
    
    # Pagination
    skip = (page - 1) * page_size
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(page_size).all()
    
    # Format response
    result = []
    for ticket in tickets:
        creator = db.query(User).filter(User.id == ticket.creator_id).first()
        agent = db.query(User).filter(User.id == ticket.assigned_to).first() if ticket.assigned_to else None
        
        result.append({
            **ticket.__dict__,
            "creator_name": creator.full_name if creator else "Unknown",
            "assigned_agent_name": agent.full_name if agent else None
        })
    
    return result


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ticket details with messages
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions (customers can only see their own tickets)
    if not current_user.is_agent and ticket.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket"
        )
    
    # Get creator and agent info
    creator = db.query(User).filter(User.id == ticket.creator_id).first()
    agent = db.query(User).filter(User.id == ticket.assigned_to).first() if ticket.assigned_to else None
    
    # Get messages
    messages = db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at).all()
    
    message_responses = []
    for msg in messages:
        # Skip internal messages for customers
        if not current_user.is_agent and msg.is_internal:
            continue
        
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        message_responses.append({
            **msg.__dict__,
            "sender_name": sender.full_name if sender else "Unknown",
            "sender_role": sender.role.value if sender else "unknown"
        })
    
    return {
        **ticket.__dict__,
        "creator_name": creator.full_name if creator else "Unknown",
        "assigned_agent_name": agent.full_name if agent else None,
        "messages": message_responses
    }


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: UUID,
    ticket_update: TicketUpdate,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Update ticket (agents only)
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update fields
    if ticket_update.subject:
        ticket.subject = ticket_update.subject
    if ticket_update.description:
        ticket.description = ticket_update.description
    if ticket_update.status:
        ticket.status = ticket_update.status
    if ticket_update.priority:
        ticket.priority = ticket_update.priority
    if ticket_update.category:
        ticket.category = ticket_update.category
    if ticket_update.assigned_to:
        ticket.assigned_to = ticket_update.assigned_to
    
    ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    
    # Get related info
    creator = db.query(User).filter(User.id == ticket.creator_id).first()
    agent = db.query(User).filter(User.id == ticket.assigned_to).first() if ticket.assigned_to else None
    
    return {
        **ticket.__dict__,
        "creator_name": creator.full_name if creator else "Unknown",
        "assigned_agent_name": agent.full_name if agent else None
    }


@router.post("/{ticket_id}/assign", response_model=SuccessResponse)
async def assign_ticket(
    ticket_id: UUID,
    assign_data: TicketAssign,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Assign ticket to agent
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Verify agent exists
    agent = db.query(User).filter(User.id == assign_data.agent_id).first()
    if not agent or not agent.is_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    ticket.assigned_to = assign_data.agent_id
    ticket.status = TicketStatus.in_progress
    db.commit()
    
    return SuccessResponse(message=f"Ticket assigned to {agent.full_name}")


@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse)
async def add_ticket_message(
    ticket_id: UUID,
    message_data: TicketMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add message to ticket
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions
    if not current_user.is_agent and ticket.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Customers cannot create internal notes
    if not current_user.is_agent and message_data.is_internal:
        message_data.is_internal = False
    
    # Analyze sentiment
    sentiment_analysis = sentiment_service.analyze_sentiment(message_data.content)
    
    # Create message
    new_message = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        content=message_data.content,
        is_internal=message_data.is_internal,
        ai_sentiment=sentiment_analysis['sentiment']
    )
    
    db.add(new_message)
    
    # Update ticket
    ticket.response_count += 1
    ticket.updated_at = datetime.utcnow()
    
    # Set first response time if not set
    if not ticket.first_response_at and current_user.is_agent:
        ticket.first_response_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    return {
        **new_message.__dict__,
        "sender_name": current_user.full_name,
        "sender_role": current_user.role.value
    }


@router.post("/{ticket_id}/close", response_model=SuccessResponse)
async def close_ticket(
    ticket_id: UUID,
    close_data: TicketClose,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Close ticket (agents only)
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket.status = TicketStatus.closed
    ticket.closed_at = datetime.utcnow()
    
    # Calculate resolution time
    if ticket.created_at:
        resolution_time = (datetime.utcnow() - ticket.created_at).total_seconds() / 60
        ticket.resolution_time_minutes = int(resolution_time)
    
    # Set satisfaction score if provided
    if close_data.customer_satisfaction_score:
        ticket.customer_satisfaction_score = close_data.customer_satisfaction_score
    
    db.commit()
    
    return SuccessResponse(message="Ticket closed successfully")


@router.get("/stats/overview", response_model=TicketStats)
async def get_ticket_stats(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get ticket statistics (agents only)
    """
    total = db.query(func.count(Ticket.id)).scalar()
    open_count = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.open).scalar()
    in_progress = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.in_progress).scalar()
    resolved = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.resolved).scalar()
    closed = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.closed).scalar()
    
    # Average response time
    avg_response = db.query(func.avg(
        func.extract('epoch', Ticket.first_response_at - Ticket.created_at) / 60
    )).filter(Ticket.first_response_at.isnot(None)).scalar()
    
    # Average resolution time
    avg_resolution = db.query(func.avg(Ticket.resolution_time_minutes)).filter(
        Ticket.resolution_time_minutes.isnot(None)
    ).scalar()
    
    # Average satisfaction
    avg_satisfaction = db.query(func.avg(Ticket.customer_satisfaction_score)).filter(
        Ticket.customer_satisfaction_score.isnot(None)
    ).scalar()
    
    return TicketStats(
        total_tickets=total or 0,
        open_tickets=open_count or 0,
        in_progress_tickets=in_progress or 0,
        resolved_tickets=resolved or 0,
        closed_tickets=closed or 0,
        avg_response_time_minutes=float(avg_response) if avg_response else None,
        avg_resolution_time_minutes=float(avg_resolution) if avg_resolution else None,
        avg_satisfaction_score=float(avg_satisfaction) if avg_satisfaction else None
    )
