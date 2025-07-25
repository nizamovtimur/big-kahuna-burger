import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import ChatSession as ChatSessionModel, Applicant as ApplicantModel, Job as JobModel
from ..schemas.schemas import ChatSessionCreate, ChatSessionResponse, ChatSession
from ..services.openai_service import OpenAIService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatSessionResponse)
async def chat_with_ai(
    chat_data: ChatSessionCreate,
    applicant_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Chat with AI about jobs. Can be used by anonymous users or authenticated applicants.
    """
    applicant = None
    job = None
    
    # If applicant email is provided, try to find/create applicant
    if applicant_email:
        applicant = db.query(ApplicantModel).filter(
            ApplicantModel.email == applicant_email
        ).first()
    
    # Get job info if job_id is provided
    job_info = None
    if chat_data.job_id:
        job = db.query(JobModel).filter(JobModel.id == chat_data.job_id).first()
        if job:
            job_info = {
                "title": job.title,
                "description": job.description,
                "department": job.department,
                "location": job.location,
                "requirements": job.requirements
            }
    
    # Get chat history for context
    chat_history = []
    session_id = None
    
    if applicant:
        # Find existing chat session
        existing_session = db.query(ChatSessionModel).filter(
            ChatSessionModel.applicant_id == applicant.id,
            ChatSessionModel.job_id == chat_data.job_id
        ).first()
        
        if existing_session:
            session_id = existing_session.id
            try:
                session_data = json.loads(existing_session.session_data)
                chat_history = session_data.get("messages", [])
            except json.JSONDecodeError:
                chat_history = []
    
    # Generate AI response
    ai_response = OpenAIService.chat_about_job(
        message=chat_data.message,
        job_info=job_info,
        chat_history=chat_history
    )
    
    # Update chat history
    chat_history.append({"role": "user", "content": chat_data.message})
    chat_history.append({"role": "assistant", "content": ai_response})
    
    # Save chat session if applicant exists
    if applicant:
        session_data = {"messages": chat_history}
        
        if session_id:
            # Update existing session
            existing_session.session_data = json.dumps(session_data)
            db.commit()
        else:
            # Create new session
            new_session = ChatSessionModel(
                applicant_id=applicant.id,
                job_id=chat_data.job_id,
                session_data=json.dumps(session_data)
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
    
    return ChatSessionResponse(
        message=ai_response,
        session_id=session_id or 0
    )


@router.get("/history", response_model=List[ChatSession])
async def get_chat_history(
    applicant_email: str,
    db: Session = Depends(get_db)
):
    """Get chat history for an applicant"""
    applicant = db.query(ApplicantModel).filter(
        ApplicantModel.email == applicant_email
    ).first()
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    sessions = db.query(ChatSessionModel).filter(
        ChatSessionModel.applicant_id == applicant.id
    ).all()
    
    return sessions


@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get messages from a specific chat session"""
    session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    try:
        session_data = json.loads(session.session_data)
        return session_data.get("messages", [])
    except json.JSONDecodeError:
        return [] 