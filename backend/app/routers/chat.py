from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from ..database import get_db
from ..models.models import ChatSession, ChatMessage, Job, User, JobApplication
from ..schemas.schemas import (
    SendMessageRequest, SendMessageResponse, ChatSessionResponse, 
    ChatMessageResponse, ChatSessionCreate
)
from ..services.auth import get_current_user
from ..services.openai_service import openai_service
import os

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
    
    # Handle apply mode - save additional responses to existing application
    if request.mode == "apply" and session.job_id and request.message.strip():
        job = db.query(Job).filter(Job.id == session.job_id).first()
        if job:
            existing_app = db.query(JobApplication).filter(
                JobApplication.user_id == current_user.id,
                JobApplication.job_id == job.id
            ).first()
            
            if existing_app:
                print(f"[DEBUG] Saving apply mode response to existing application")
                # Get current additional_answers or initialize empty dict
                current_answers = existing_app.additional_answers or {}
                
                # Add new response with timestamp
                timestamp = datetime.now().isoformat()
                response_key = f"chat_response_{timestamp}"
                
                current_answers[response_key] = {
                    "message": request.message,
                    "timestamp": timestamp,
                    "context": "follow_up_chat",
                    "endpoint": "send"
                }
                
                # Update the application
                existing_app.additional_answers = current_answers
                # Force SQLAlchemy to detect JSON field changes

                flag_modified(existing_app, 'additional_answers')
                db.commit()
                
                print(f"[DEBUG] Updated existing application from /send endpoint:")
                print(f"  application_id: {existing_app.id}")
                print(f"  new_response: {request.message[:100]}...")
    
    # Get chat history from session
    chat_history = _get_session_messages(db=db, session=session)
    
    # Prepare enhanced message for AI (add mode context)
    enhanced_message = request.message
    if request.mode == "apply" and session.job_id:
        job = db.query(Job).filter(Job.id == session.job_id).first()
        if job:
            enhanced_message += f"\n\n[Контекст: Пользователь подает заявку на позицию '{job.title}'. Проведите собеседование.]"
    elif request.mode == "discussion" and session.job_id:
        job = db.query(Job).filter(Job.id == session.job_id).first()
        if job:
            enhanced_message += f"\n\n[Контекст: Пользователь обсуждает вакансию '{job.title}'. Ответьте на вопросы о позиции.]"
    
    # Get AI response
    ai_response = await openai_service.chat_with_ai(
        user_message=enhanced_message,
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

@router.post("/send-with-file", response_model=SendMessageResponse)
async def send_message_with_file(
    message: str = Form(""),
    session_id: int = Form(None),
    job_id: int = Form(None),
    mode: str = Form("discussion"),
    cv_file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"[DEBUG] send_message_with_file called:")
    print(f"  message: {message}")
    print(f"  session_id: {session_id}")
    print(f"  job_id: {job_id}")
    print(f"  mode: {mode}")
    print(f"  cv_file: {cv_file.filename if cv_file else None}")
    print(f"  user_id: {current_user.id}")
    """
    Send message to AI assistant with optional file upload (for applications).
    WARNING: This endpoint is vulnerable to prompt injection and file upload attacks!
    """
    
    # Get or create session
    session = _get_or_create_session(
        db=db, 
        user_id=current_user.id, 
        session_id=session_id,
        job_id=job_id
    )
    
    # Get job context if session has job_id
    job_context = None
    job = None
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
    
    # Handle file upload if in apply mode
    file_info = None
    cv_score = None
    
    print(f"[DEBUG] File processing check:")
    print(f"  cv_file exists: {cv_file is not None}")
    print(f"  mode == 'apply': {mode == 'apply'}")
    print(f"  job exists: {job is not None}")
    if job:
        print(f"  job.id: {job.id}")
    
    if cv_file and mode == "apply" and job:
        print(f"[DEBUG] Processing CV file for job application")
        # Check if user already applied to this job
        existing_app = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id,
            JobApplication.job_id == job.id
        ).first()
        
        print(f"[DEBUG] Existing application: {existing_app is not None}")
        
        if existing_app:
            print(f"[DEBUG] User already applied, updating with additional info")
            # User already applied, save additional responses to existing application
            if message and message.strip():
                # Get current additional_answers or initialize empty dict
                current_answers = existing_app.additional_answers or {}
                
                # Add new response with timestamp
                timestamp = datetime.now().isoformat()
                response_key = f"chat_response_{timestamp}"
                
                current_answers[response_key] = {
                    "message": message,
                    "timestamp": timestamp,
                    "context": "follow_up_chat"
                }
                
                # Update the application
                existing_app.additional_answers = current_answers
                # Force SQLAlchemy to detect JSON field changes

                flag_modified(existing_app, 'additional_answers')
                db.commit()
                
                print(f"[DEBUG] Updated existing application with additional info:")
                print(f"  application_id: {existing_app.id}")
                print(f"  new_response: {message[:100]}...")
                
                file_info = {
                    "updated_existing": True,
                    "application_id": existing_app.id,
                    "response_saved": True
                }
        else:
            print(f"[DEBUG] Creating new job application")
            # Process CV file (vulnerable implementation)
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, f"{current_user.id}_{job.id}_{cv_file.filename}")
            
            # Save file (vulnerable - no validation!)
            with open(file_path, "wb") as buffer:
                content = await cv_file.read()
                buffer.write(content)
            
            # Extract text from PDF and analyze CV
            try:
                cv_text = openai_service.extract_text_from_pdf(content)
                cv_score = await openai_service.analyze_cv(cv_text, job.description)
                
                # Create job application
                application = JobApplication(
                    user_id=current_user.id,
                    job_id=job.id,
                    cover_letter=message or "Заявка подана через чат",
                    cv_filename=cv_file.filename,
                    cv_score=cv_score,
                    additional_answers={"submitted_via_chat": True},
                    status="pending"
                )
                
                db.add(application)
                db.commit()
                db.refresh(application)
                
                print(f"[DEBUG] Job application created successfully:")
                print(f"  application_id: {application.id}")
                print(f"  cv_score: {cv_score}")
                
                file_info = {
                    "filename": cv_file.filename,
                    "cv_score": cv_score,
                    "application_id": application.id
                }
                
            except Exception as e:
                print(f"[DEBUG] Error processing CV: {e}")
                file_info = {"error": str(e)}
    else:
        print(f"[DEBUG] File processing skipped - conditions not met")
    
    # Get chat history from session
    chat_history = _get_session_messages(db=db, session=session)
    
    # Prepare enhanced message for AI
    enhanced_message = message
    if file_info:
        if file_info.get("cv_score"):
            enhanced_message += f"\n\n[Система: Пользователь прикрепил резюме '{file_info['filename']}'. Оценка резюме: {file_info['cv_score']}/10. Задайте пользователю дополнительные вопросы о его опыте и навыках.]"
        elif file_info.get("error"):
            enhanced_message += f"\n\n[Система: Ошибка при обработке файла: {file_info['error']}]"
    
    # Add mode context to message
    if mode == "apply" and job:
        enhanced_message += f"\n\n[Контекст: Пользователь подает заявку на позицию '{job.title}'. Проведите собеседование.]"
    elif mode == "discussion" and job:
        enhanced_message += f"\n\n[Контекст: Пользователь обсуждает вакансию '{job.title}'. Ответьте на вопросы о позиции.]"
    
    # Get AI response
    ai_response = await openai_service.chat_with_ai(
        user_message=enhanced_message,
        job_context=job_context,
        chat_history=chat_history
    )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=message + (f" [Прикрепил файл: {cv_file.filename}]" if cv_file else "")
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
            messages=[]
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