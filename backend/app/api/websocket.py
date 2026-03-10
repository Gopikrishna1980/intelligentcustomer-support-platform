"""
WebSocket endpoint for real-time chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
from datetime import datetime

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.services.ai_service import ai_service
from app.services.sentiment_service import sentiment_service
from app.services.rag_service import rag_service

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # session_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # user_id -> WebSocket (for agent dashboard)
        self.agent_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect client to chat session"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect client from chat session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Send message to all clients in session"""
        if session_id in self.active_connections:
            dead_connections = set()
            
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Remove dead connections
            for conn in dead_connections:
                self.active_connections[session_id].discard(conn)
    
    async def connect_agent(self, websocket: WebSocket, user_id: str):
        """Connect agent to dashboard"""
        await websocket.accept()
        self.agent_connections[user_id] = websocket
    
    def disconnect_agent(self, user_id: str):
        """Disconnect agent from dashboard"""
        if user_id in self.agent_connections:
            del self.agent_connections[user_id]
    
    async def notify_agents(self, message: dict):
        """Notify all connected agents"""
        dead_connections = []
        
        for user_id, connection in self.agent_connections.items():
            try:
                await connection.send_json(message)
            except:
                dead_connections.append(user_id)
        
        # Remove dead connections
        for user_id in dead_connections:
            del self.agent_connections[user_id]


manager = ConnectionManager()


async def get_user_from_token(token: str, db: Session) -> User:
    """Verify JWT token and get user"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except:
        return None


@router.websocket("/chat/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat
    
    Client sends:
    {
        "type": "message",
        "content": "Hello, I need help with..."
    }
    
    {
        "type": "typing",
        "is_typing": true
    }
    
    Server sends:
    {
        "type": "message",
        "sender": "agent",
        "sender_name": "John Doe",
        "content": "How can I help you?",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    {
        "type": "typing",
        "sender_name": "Agent John"
    }
    
    {
        "type": "agent_joined",
        "agent_name": "John Doe"
    }
    """
    # Verify user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    # Verify session exists
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Check permissions
    if not user.is_agent and session.user_id != user.id:
        await websocket.close(code=1008, reason="Forbidden")
        return
    
    # Connect
    await manager.connect(websocket, session_id)
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "Connected to chat"
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                content = data.get("content")
                
                if not content:
                    continue
                
                # Analyze sentiment
                sentiment_analysis = sentiment_service.analyze_sentiment(content)
                
                # Determine sender type
                sender_type = "agent" if user.is_agent else "customer"
                
                # Create message in database
                new_message = ChatMessage(
                    session_id=session.id,
                    sender_id=user.id,
                    sender_type=sender_type,
                    content=content,
                    is_ai_generated=False,
                    ai_sentiment=sentiment_analysis['sentiment']
                )
                
                db.add(new_message)
                session.message_count += 1
                
                if sender_type == "agent":
                    session.agent_message_count += 1
                    
                    # Mark agent joined if first message
                    if session.is_bot_only:
                        session.is_bot_only = False
                        session.agent_id = user.id
                        session.agent_joined_at = datetime.utcnow()
                        
                        # Broadcast agent joined
                        await manager.broadcast_to_session(session_id, {
                            "type": "agent_joined",
                            "agent_name": user.full_name
                        })
                
                session.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(new_message)
                
                # Broadcast message to all clients in session
                await manager.broadcast_to_session(session_id, {
                    "type": "message",
                    "message_id": str(new_message.id),
                    "sender": sender_type,
                    "sender_name": user.full_name,
                    "content": content,
                    "sentiment": sentiment_analysis['sentiment'],
                    "timestamp": new_message.created_at.isoformat()
                })
                
                # If customer message in bot-only mode, generate AI response
                if sender_type == "customer" and session.is_bot_only:
                    # Get conversation history
                    history = db.query(ChatMessage).filter(
                        ChatMessage.session_id == session.id
                    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
                    
                    conversation_history = []
                    for msg in reversed(history):
                        role = "assistant" if msg.sender_type == "bot" else "user"
                        conversation_history.append({"role": role, "content": msg.content})
                    
                    # Get KB context
                    kb_context = await rag_service.get_relevant_context(content)
                    
                    # Generate AI response
                    ai_response = await ai_service.chat_response(
                        content,
                        conversation_history=conversation_history,
                        context=kb_context
                    )
                    
                    # Create bot message
                    bot_message = ChatMessage(
                        session_id=session.id,
                        sender_type="bot",
                        content=ai_response['response'],
                        is_ai_generated=True,
                        ai_confidence=ai_response.get('confidence', 0)
                    )
                    
                    db.add(bot_message)
                    session.message_count += 1
                    session.bot_message_count += 1
                    db.commit()
                    db.refresh(bot_message)
                    
                    # Broadcast bot response
                    await manager.broadcast_to_session(session_id, {
                        "type": "message",
                        "message_id": str(bot_message.id),
                        "sender": "bot",
                        "sender_name": "AI Assistant",
                        "content": ai_response['response'],
                        "confidence": ai_response.get('confidence'),
                        "timestamp": bot_message.created_at.isoformat()
                    })
                    
                    # Check if escalation needed
                    if ai_response.get('should_escalate'):
                        await manager.broadcast_to_session(session_id, {
                            "type": "escalation_suggested",
                            "message": "Would you like to speak with a human agent?"
                        })
                        
                        # Notify agents
                        await manager.notify_agents({
                            "type": "escalation_request",
                            "session_id": session_id,
                            "user_name": user.full_name
                        })
            
            elif message_type == "typing":
                is_typing = data.get("is_typing", False)
                
                # Broadcast typing indicator
                await manager.broadcast_to_session(session_id, {
                    "type": "typing",
                    "sender_name": user.full_name,
                    "is_typing": is_typing
                })
            
            elif message_type == "request_agent":
                # Customer requests human agent
                session.ai_intent = "agent_requested"
                db.commit()
                
                # Notify all agents
                await manager.notify_agents({
                    "type": "agent_request",
                    "session_id": session_id,
                    "user_name": user.full_name,
                    "message": f"{user.full_name} is requesting a human agent"
                })
                
                await websocket.send_json({
                    "type": "notification",
                    "message": "We're notifying available agents. Someone will join shortly."
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        
        # Broadcast user disconnected
        await manager.broadcast_to_session(session_id, {
            "type": "user_disconnected",
            "user_name": user.full_name
        })


@router.websocket("/agent")
async def agent_dashboard_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for agent dashboard
    
    Receives real-time notifications:
    - New tickets
    - New chat requests
    - Ticket updates
    - Escalations
    """
    # Verify agent
    user = await get_user_from_token(token, db)
    if not user or not user.is_agent:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    # Connect agent
    await manager.connect_agent(websocket, str(user.id))
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to agent dashboard"
    })
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_json()
            
            # Agent can send ping to keep alive
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect_agent(str(user.id))
        
        # Update agent offline status
        user.is_online = False
        db.commit()


# Export connection manager for use in other modules
__all__ = ["router", "manager"]
