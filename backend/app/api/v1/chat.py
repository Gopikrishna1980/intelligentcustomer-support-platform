"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import secrets

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_agent
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate,
    ChatMessageCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatSessionListResponse,
    ChatSessionEnd,
    ChatStats
)
from app.schemas.common import SuccessResponse
from app.services.ai_service import ai_service
from app.services.sentiment_service import sentiment_service
from app.services.rag_service import rag_service

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new chat session
    
    - Creates session with unique ID
    - Starts with bot-only mode
    - Can send initial message
    """
    # Generate unique session ID
    session_id = f"chat-{secrets.token_urlsafe(16)}"
    
    # Create session
    new_session = ChatSession(
        session_id=session_id,
        user_id=current_user.id,
        is_active=True,
        is_bot_only=True,
        user_ip=session_data.user_ip,
        user_agent=session_data.user_agent,
        page_url=session_data.page_url
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Send initial message if provided
    if session_data.initial_message:
        # Analyze sentiment and intent
        sentiment_analysis = sentiment_service.analyze_sentiment(session_data.initial_message)
        ai_intent = await ai_service.extract_intent(session_data.initial_message)
        
        # Create user message
        user_message = ChatMessage(
            session_id=new_session.id,
            sender_id=current_user.id,
            sender_type="customer",
            content=session_data.initial_message,
            is_ai_generated=False,
            ai_sentiment=sentiment_analysis['sentiment']
        )
        db.add(user_message)
        
        # Get KB context
        kb_context = await rag_service.get_relevant_context(session_data.initial_message)
        
        # Generate AI response
        ai_response = await ai_service.chat_response(
            session_data.initial_message,
            context=kb_context
        )
        
        # Create bot message
        bot_message = ChatMessage(
            session_id=new_session.id,
            sender_type="bot",
            content=ai_response['response'],
            is_ai_generated=True,
            ai_confidence=ai_response.get('confidence', 0)
        )
        db.add(bot_message)
        
        # Update session
        new_session.message_count = 2
        new_session.bot_message_count = 1
        new_session.ai_intent = ai_intent
        new_session.ai_sentiment = sentiment_analysis['sentiment']
        
        db.commit()
    
    return {
        **new_session.__dict__,
        "agent_name": None,
        "messages": None
    }


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    include_messages: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat session details
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check permissions
    if not current_user.is_agent and session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get messages if requested
    messages = None
    if include_messages:
        msg_list = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        messages = []
        for msg in msg_list:
            sender = None
            if msg.sender_id:
                sender = db.query(User).filter(User.id == msg.sender_id).first()
            
            messages.append({
                **msg.__dict__,
                "sender_name": sender.full_name if sender else ("AI Assistant" if msg.sender_type == "bot" else "Unknown")
            })
    
    # Get agent info
    agent = None
    if session.agent_id:
        agent = db.query(User).filter(User.id == session.agent_id).first()
    
    return {
        **session.__dict__,
        "agent_name": agent.full_name if agent else None,
        "messages": messages
    }


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: UUID,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message in chat session
    
    - Customer messages get AI response automatically
    - Agent messages mark session as human-handled
    - Analyzes sentiment
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat session has ended"
        )
    
    # Check permissions
    if not current_user.is_agent and session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Analyze sentiment
    sentiment_analysis = sentiment_service.analyze_sentiment(message_data.content)
    
    # Determine sender type
    if current_user.is_agent:
        sender_type = "agent"
        
        # If agent joins for first time
        if session.is_bot_only:
            session.is_bot_only = False
            session.agent_id = current_user.id
            session.agent_joined_at = datetime.utcnow()
    else:
        sender_type = "customer"
    
    # Create message
    new_message = ChatMessage(
        session_id=session_id,
        sender_id=current_user.id,
        sender_type=sender_type,
        content=message_data.content,
        is_ai_generated=False,
        ai_sentiment=sentiment_analysis['sentiment']
    )
    
    db.add(new_message)
    
    # Update session counts
    session.message_count += 1
    if sender_type == "agent":
        session.agent_message_count += 1
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    # If customer message and bot-only mode, generate AI response
    if sender_type == "customer" and session.is_bot_only:
        # Get conversation history
        history = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        conversation_history = []
        for msg in reversed(history):
            role = "assistant" if msg.sender_type == "bot" else "user"
            conversation_history.append({"role": role, "content": msg.content})
        
        # Get KB context
        kb_context = await rag_service.get_relevant_context(message_data.content)
        
        # Generate AI response
        ai_response = await ai_service.chat_response(
            message_data.content,
            conversation_history=conversation_history,
            context=kb_context
        )
        
        # Create bot message
        bot_message = ChatMessage(
            session_id=session_id,
            sender_type="bot",
            content=ai_response['response'],
            is_ai_generated=True,
            ai_confidence=ai_response.get('confidence', 0)
        )
        db.add(bot_message)
        
        session.message_count += 1
        session.bot_message_count += 1
        
        # Check if escalation needed
        if ai_response.get('should_escalate'):
            session.ai_intent = "escalation_needed"
        
        db.commit()
    
    return {
        **new_message.__dict__,
        "sender_name": current_user.full_name
    }


@router.post("/sessions/{session_id}/end", response_model=SuccessResponse)
async def end_chat_session(
    session_id: UUID,
    end_data: ChatSessionEnd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End chat session
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check permissions
    if not current_user.is_agent and session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    session.is_active = False
    session.ended_at = datetime.utcnow()
    
    if end_data.satisfaction_score:
        session.satisfaction_score = end_data.satisfaction_score
    
    db.commit()
    
    return SuccessResponse(message="Chat session ended")


@router.get("/sessions", response_model=List[ChatSessionListResponse])
async def list_chat_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    my_sessions: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List chat sessions
    """
    query = db.query(ChatSession)
    
    # Filters
    if is_active is not None:
        query = query.filter(ChatSession.is_active == is_active)
    
    if my_sessions:
        if current_user.is_agent:
            query = query.filter(ChatSession.agent_id == current_user.id)
        else:
            query = query.filter(ChatSession.user_id == current_user.id)
    elif not current_user.is_agent:
        # Regular users only see their own sessions
        query = query.filter(ChatSession.user_id == current_user.id)
    
    # Pagination
    skip = (page - 1) * page_size
    sessions = query.order_by(ChatSession.created_at.desc()).offset(skip).limit(page_size).all()
    
    # Format response
    result = []
    for session in sessions:
        user = db.query(User).filter(User.id == session.user_id).first()
        agent = db.query(User).filter(User.id == session.agent_id).first() if session.agent_id else None
        
        result.append({
            **session.__dict__,
            "user_name": user.full_name if user else "Unknown",
            "agent_name": agent.full_name if agent else None
        })
    
    return result


@router.get("/stats/overview", response_model=ChatStats)
async def get_chat_stats(
    current_user: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Get chat statistics (agents only)
    """
    from sqlalchemy import func
    
    total = db.query(func.count(ChatSession.id)).scalar()
    active = db.query(func.count(ChatSession.id)).filter(ChatSession.is_active == True).scalar()
    bot_only = db.query(func.count(ChatSession.id)).filter(ChatSession.is_bot_only == True).scalar()
    with_agent = db.query(func.count(ChatSession.id)).filter(ChatSession.agent_id.isnot(None)).scalar()
    
    avg_messages = db.query(func.avg(ChatSession.message_count)).scalar()
    avg_satisfaction = db.query(func.avg(ChatSession.satisfaction_score)).filter(
        ChatSession.satisfaction_score.isnot(None)
    ).scalar()
    
    total_messages = db.query(func.sum(ChatSession.message_count)).scalar()
    
    return ChatStats(
        total_sessions=total or 0,
        active_sessions=active or 0,
        bot_only_sessions=bot_only or 0,
        with_agent_sessions=with_agent or 0,
        avg_messages_per_session=float(avg_messages) if avg_messages else 0.0,
        avg_session_duration_minutes=None,  # Would need to calculate
        avg_satisfaction_score=float(avg_satisfaction) if avg_satisfaction else None,
        total_messages=int(total_messages) if total_messages else 0
    )
