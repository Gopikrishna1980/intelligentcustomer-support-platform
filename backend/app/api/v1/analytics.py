"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_agent
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.chat import ChatSession
from pydantic import BaseModel

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard overview statistics"""
    # Tickets
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_today: int
    avg_response_time_hours: Optional[float]
    avg_resolution_time_hours: Optional[float]
    
    # Chat
    active_chat_sessions: int
    total_chat_sessions_today: int
    avg_chat_satisfaction: Optional[float]
    
    # Agents
    online_agents: int
    total_agents: int
    busiest_agent: Optional[str]
    
    # Satisfaction
    avg_ticket_satisfaction: Optional[float]
    satisfaction_trend: str  # improving, declining, stable


class TicketTrendData(BaseModel):
    """Time-series ticket data"""
    date: str
    created: int
    resolved: int
    open: int


class CategoryDistribution(BaseModel):
    """Tickets by category"""
    category: str
    count: int
    percentage: float


class AgentPerformance(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    assigned_tickets: int
    resolved_tickets: int
    avg_resolution_time_hours: Optional[float]
    avg_satisfaction: Optional[float]
    current_workload: int


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview statistics
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Ticket stats
    total_tickets = db.query(func.count(Ticket.id)).scalar() or 0
    open_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.open
    ).scalar() or 0
    in_progress = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.in_progress
    ).scalar() or 0
    resolved_today = db.query(func.count(Ticket.id)).filter(
        and_(
            Ticket.status == TicketStatus.resolved,
            Ticket.resolved_at >= today_start
        )
    ).scalar() or 0
    
    # Average times
    avg_response_minutes = db.query(
        func.avg(func.extract('epoch', Ticket.first_response_at - Ticket.created_at) / 60)
    ).filter(Ticket.first_response_at.isnot(None)).scalar()
    
    avg_resolution_minutes = db.query(
        func.avg(Ticket.resolution_time_minutes)
    ).filter(Ticket.resolution_time_minutes.isnot(None)).scalar()
    
    # Chat stats
    active_chats = db.query(func.count(ChatSession.id)).filter(
        ChatSession.is_active == True
    ).scalar() or 0
    
    chats_today = db.query(func.count(ChatSession.id)).filter(
        ChatSession.created_at >= today_start
    ).scalar() or 0
    
    avg_chat_satisfaction = db.query(func.avg(ChatSession.satisfaction_score)).filter(
        ChatSession.satisfaction_score.isnot(None)
    ).scalar()
    
    # Agent stats
    online_agents = db.query(func.count(User.id)).filter(
        and_(
            User.is_agent == True,
            User.is_online == True
        )
    ).scalar() or 0
    
    total_agents = db.query(func.count(User.id)).filter(
        User.is_agent == True
    ).scalar() or 0
    
    # Busiest agent
    busiest = db.query(
        User.full_name,
        func.count(Ticket.id).label('ticket_count')
    ).join(Ticket, Ticket.assigned_to == User.id).filter(
        Ticket.status.in_([TicketStatus.open, TicketStatus.in_progress])
    ).group_by(User.id, User.full_name).order_by(
        func.count(Ticket.id).desc()
    ).first()
    
    # Ticket satisfaction
    avg_ticket_satisfaction = db.query(
        func.avg(Ticket.customer_satisfaction_score)
    ).filter(Ticket.customer_satisfaction_score.isnot(None)).scalar()
    
    # Satisfaction trend (compare last 7 days vs previous 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    
    recent_satisfaction = db.query(
        func.avg(Ticket.customer_satisfaction_score)
    ).filter(
        and_(
            Ticket.customer_satisfaction_score.isnot(None),
            Ticket.closed_at >= seven_days_ago
        )
    ).scalar()
    
    previous_satisfaction = db.query(
        func.avg(Ticket.customer_satisfaction_score)
    ).filter(
        and_(
            Ticket.customer_satisfaction_score.isnot(None),
            Ticket.closed_at >= fourteen_days_ago,
            Ticket.closed_at < seven_days_ago
        )
    ).scalar()
    
    if recent_satisfaction and previous_satisfaction:
        if recent_satisfaction > previous_satisfaction + 0.2:
            satisfaction_trend = "improving"
        elif recent_satisfaction < previous_satisfaction - 0.2:
            satisfaction_trend = "declining"
        else:
            satisfaction_trend = "stable"
    else:
        satisfaction_trend = "insufficient_data"
    
    return DashboardStats(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress,
        resolved_today=resolved_today,
        avg_response_time_hours=float(avg_response_minutes / 60) if avg_response_minutes else None,
        avg_resolution_time_hours=float(avg_resolution_minutes / 60) if avg_resolution_minutes else None,
        active_chat_sessions=active_chats,
        total_chat_sessions_today=chats_today,
        avg_chat_satisfaction=float(avg_chat_satisfaction) if avg_chat_satisfaction else None,
        online_agents=online_agents,
        total_agents=total_agents,
        busiest_agent=busiest[0] if busiest else None,
        avg_ticket_satisfaction=float(avg_ticket_satisfaction) if avg_ticket_satisfaction else None,
        satisfaction_trend=satisfaction_trend
    )


@router.get("/tickets/trends", response_model=List[TicketTrendData])
async def get_ticket_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get ticket volume trends over time
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Group by date
    created_by_date = db.query(
        func.date(Ticket.created_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(func.date(Ticket.created_at)).all()
    
    resolved_by_date = db.query(
        func.date(Ticket.resolved_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.resolved_at >= start_date
    ).group_by(func.date(Ticket.resolved_at)).all()
    
    # Create date map
    created_map = {str(row.date): row.count for row in created_by_date}
    resolved_map = {str(row.date): row.count for row in resolved_by_date}
    
    # Generate all dates
    trends = []
    current_date = start_date.date()
    end_date = datetime.utcnow().date()
    
    cumulative_open = 0
    
    while current_date <= end_date:
        date_str = str(current_date)
        created = created_map.get(date_str, 0)
        resolved = resolved_map.get(date_str, 0)
        cumulative_open += (created - resolved)
        
        trends.append(TicketTrendData(
            date=date_str,
            created=created,
            resolved=resolved,
            open=max(0, cumulative_open)
        ))
        
        current_date += timedelta(days=1)
    
    return trends


@router.get("/tickets/by-category", response_model=List[CategoryDistribution])
async def get_tickets_by_category(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get ticket distribution by category
    """
    total = db.query(func.count(Ticket.id)).scalar() or 1  # Avoid division by zero
    
    category_counts = db.query(
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.category).all()
    
    distribution = []
    for category, count in category_counts:
        distribution.append(CategoryDistribution(
            category=category.value,
            count=count,
            percentage=round((count / total) * 100, 2)
        ))
    
    return distribution


@router.get("/agents/performance", response_model=List[AgentPerformance])
async def get_agent_performance(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for all agents
    """
    agents = db.query(User).filter(User.is_agent == True).all()
    
    performance = []
    
    for agent in agents:
        # Total assigned tickets
        assigned = db.query(func.count(Ticket.id)).filter(
            Ticket.assigned_to == agent.id
        ).scalar() or 0
        
        # Resolved tickets
        resolved = db.query(func.count(Ticket.id)).filter(
            and_(
                Ticket.assigned_to == agent.id,
                Ticket.status == TicketStatus.resolved
            )
        ).scalar() or 0
        
        # Average resolution time
        avg_resolution = db.query(
            func.avg(Ticket.resolution_time_minutes)
        ).filter(
            and_(
                Ticket.assigned_to == agent.id,
                Ticket.resolution_time_minutes.isnot(None)
            )
        ).scalar()
        
        # Average satisfaction
        avg_satisfaction = db.query(
            func.avg(Ticket.customer_satisfaction_score)
        ).filter(
            and_(
                Ticket.assigned_to == agent.id,
                Ticket.customer_satisfaction_score.isnot(None)
            )
        ).scalar()
        
        # Current workload
        current_workload = db.query(func.count(Ticket.id)).filter(
            and_(
                Ticket.assigned_to == agent.id,
                Ticket.status.in_([TicketStatus.open, TicketStatus.in_progress])
            )
        ).scalar() or 0
        
        performance.append(AgentPerformance(
            agent_id=str(agent.id),
            agent_name=agent.full_name,
            assigned_tickets=assigned,
            resolved_tickets=resolved,
            avg_resolution_time_hours=float(avg_resolution / 60) if avg_resolution else None,
            avg_satisfaction=float(avg_satisfaction) if avg_satisfaction else None,
            current_workload=current_workload
        ))
    
    # Sort by current workload descending
    performance.sort(key=lambda x: x.current_workload, reverse=True)
    
    return performance


@router.get("/reports/export")
async def export_report(
    report_type: str = Query(..., pattern="^(tickets|agents|satisfaction)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Export analytics report
    
    TODO: Implement CSV/PDF generation
    """
    return {"message": "Report export not yet implemented", "type": report_type}
