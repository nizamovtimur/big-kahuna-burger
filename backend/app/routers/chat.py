from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import ChatSession, ChatMessage, Job, User
from ..schemas.schemas import (
    SendMessageRequest, SendMessageResponse, ChatSessionResponse, 
    ChatMessageResponse, ChatSessionCreate
)
from ..services.auth import get_current_user
from ..services.openai_service import openai_service

router = APIRouter(prefix="/chat", tags=["chat"])

def _get_or_create_session(db: Session, user_id: int, session_id: int = None, job_id: int = None) -> ChatSession:
    """
    Get existing session or create new one.
    """
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    else:
        # Create new session
        session = ChatSession(
            user_id=user_id,
            job_id=job_id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

def _get_session_messages(db: Session, session: ChatSession, limit: int = 20) -> List[dict]:
    """
    Get recent messages from session in OpenAI API format.
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message to AI assistant and get response.
    WARNING: This endpoint is vulnerable to prompt injection attacks!
    """
    # Get or create session
    session = _get_or_create_session(
        db=db, 
        user_id=current_user.id, 
        session_id=request.session_id,
        job_id=request.job_id
    )
    
    # Get job context if session has job_id
    job_context = None
    if session.job_id:
        job = db.query(Job).filter(Job.id == session.job_id).first()
        if job:
            job_context = {
                "job_title": job.title,
                "job_description": job.description,
                "job_requirements": job.requirements,
                "job_location": job.location,
                "salary_range": job.salary_range
            }
    
    # Get chat history from session
    chat_history = _get_session_messages(db=db, session=session)
    
    # Get AI response
    ai_response = await openai_service.chat_with_ai(
        user_message=request.message,
        job_context=job_context,
        chat_history=chat_history
    )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # Save AI response
    ai_message = ChatMessage(
        session_id=session.id,
        role="assistant", 
        content=ai_response
    )
    db.add(ai_message)
    
    # Update session timestamp
    session.updated_at = datetime.now()
    
    db.commit()
    db.refresh(user_message)
    db.refresh(ai_message)
    db.refresh(session)
    
    return SendMessageResponse(
        session=ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            job_id=session.job_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=[]  # Don't load all messages in response
        ),
        user_message=ChatMessageResponse(
            id=user_message.id,
            session_id=user_message.session_id,
            role=user_message.role,
            content=user_message.content,
            created_at=user_message.created_at
        ),
        ai_message=ChatMessageResponse(
            id=ai_message.id,
            session_id=ai_message.session_id,
            role=ai_message.role,
            content=ai_message.content,
            created_at=ai_message.created_at
        )
    )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's chat sessions.
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).limit(50).all()
    
    return [
        ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            job_id=session.job_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=[]  # Don't load messages by default
        )
        for session in sessions
    ]

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific chat session with all messages.
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        job_id=session.job_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific chat session and all its messages.
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.delete("/sessions")
async def delete_all_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all chat sessions for current user.
    """
    deleted_count = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} chat sessions",
        "deleted_count": deleted_count
    } 