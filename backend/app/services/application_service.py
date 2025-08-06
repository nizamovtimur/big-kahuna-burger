import os
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException, UploadFile
from ..models.models import JobApplication, Job, User
from .openai_service import openai_service


class ApplicationService:
    """
    Central service for all job application operations.
    Handles file uploads, CV analysis, and database operations.
    """
    
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def create_application_from_file(
        self,
        db: Session,
        user: User,
        job_id: int,
        cv_file: UploadFile,
        cover_letter: str = "",
        additional_answers: Optional[dict] = None
    ) -> JobApplication:
        """
        Create job application from uploaded file.
        Handles file upload, text extraction, CV scoring, and database storage.
        """
        # Check if job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if user already applied
        existing_app = self.get_existing_application(db, user.id, job_id)
        if existing_app:
            raise HTTPException(status_code=400, detail="Already applied to this job")
        
        # Save uploaded file and extract content
        file_path, cv_content = await self._save_and_extract_file(cv_file, user.id, job_id)
        
        # Analyze CV
        cv_score = await openai_service.analyze_cv(cv_content, job.description)
        
        # Create application
        application = self._create_application_record(
            db, user.id, job_id, cv_file.filename, cv_score, cover_letter, additional_answers
        )
        
        return application
    
    async def create_application_from_content(
        self,
        db: Session,
        user: User,
        job_id: int,
        cv_content: str,
        cv_filename: str,
        cover_letter: str = "",
        additional_answers: Optional[dict] = None
    ) -> JobApplication:
        """
        Create job application from CV content (used by AI agent).
        """
        # Check if job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if user already applied
        existing_app = self.get_existing_application(db, user.id, job_id)
        if existing_app:
            raise HTTPException(status_code=400, detail="Already applied to this job")
        
        # Analyze CV content
        cv_score = await openai_service.analyze_cv(cv_content, job.description)
        
        # Create application
        application = self._create_application_record(
            db, user.id, job_id, cv_filename, cv_score, cover_letter, additional_answers
        )
        
        return application
    
    def get_existing_application(self, db: Session, user_id: int, job_id: int) -> Optional[JobApplication]:
        """Get existing application for user and job."""
        return db.query(JobApplication).filter(
            JobApplication.user_id == user_id,
            JobApplication.job_id == job_id
        ).first()
    
    def save_user_response(
        self,
        db: Session,
        application: JobApplication,
        key: str,
        value: str,
        context: str = "general",
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Save user response to application.
        WARNING: Stores data without sanitization (XSS vulnerability for education).
        """
        if not application.additional_answers:
            application.additional_answers = {}
        
        # Vulnerable: Store data without sanitization
        application.additional_answers[key] = {
            "value": value,  # XSS vulnerability
            "context": context,
            "saved_at": timestamp or datetime.now().isoformat()
        }
        
        flag_modified(application, 'additional_answers')
        db.commit()
        return True
    
    def save_cv_analysis(
        self,
        db: Session,
        application: JobApplication,
        cv_score: int,
        cv_filename: str,
        analysis_context: str = "agent_analysis"
    ) -> bool:
        """Save CV analysis results to application."""
        if not application.additional_answers:
            application.additional_answers = {}
        
        application.additional_answers["cv_analysis"] = {
            "score": cv_score,
            "filename": cv_filename,
            "context": analysis_context,
            "analyzed_at": datetime.now().isoformat()
        }
        
        flag_modified(application, 'additional_answers')
        db.commit()
        return True
    
    def save_chat_response(
        self,
        db: Session,
        application: JobApplication,
        message: str,
        context: str = "follow_up_chat"
    ) -> bool:
        """
        Save chat response to application.
        WARNING: Stores message without sanitization (XSS vulnerability for education).
        """
        if not application.additional_answers:
            application.additional_answers = {}
        
        timestamp = datetime.now().isoformat()
        response_key = f"chat_response_{timestamp}"
        
        # Vulnerable: Direct storage without sanitization
        application.additional_answers[response_key] = {
            "message": message,  # XSS vulnerability
            "timestamp": timestamp,
            "context": context
        }
        
        flag_modified(application, 'additional_answers')
        db.commit()
        return True
    
    def update_application_status(
        self,
        db: Session,
        application_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update application status with optional notes."""
        application = db.query(JobApplication).filter(
            JobApplication.id == application_id
        ).first()
        
        if not application:
            return False
        
        application.status = status
        
        if notes:
            if not application.additional_answers:
                application.additional_answers = {}
            
            application.additional_answers["status_update"] = {
                "notes": notes,
                "updated_at": datetime.now().isoformat(),
                "updated_by": "system"
            }
            flag_modified(application, 'additional_answers')
        
        db.commit()
        return True
    
    async def _save_and_extract_file(self, cv_file: UploadFile, user_id: int, job_id: int) -> tuple[str, str]:
        """
        Save uploaded file and extract content.
        WARNING: No file validation (security vulnerability for education).
        """
        # Vulnerable: No file type validation, size limits, or malware scanning
        file_path = os.path.join(self.upload_dir, f"{user_id}_{job_id}_{cv_file.filename}")
        
        # Save file content
        with open(file_path, "wb") as buffer:
            content = await cv_file.read()
            buffer.write(content)
        
        # Extract text from PDF
        cv_text = openai_service.extract_text_from_pdf(content)
        
        return file_path, cv_text
    
    def _create_application_record(
        self,
        db: Session,
        user_id: int,
        job_id: int,
        cv_filename: str,
        cv_score: int,
        cover_letter: str,
        additional_answers: Optional[dict]
    ) -> JobApplication:
        """Create application database record."""
        application = JobApplication(
            user_id=user_id,
            job_id=job_id,
            cover_letter=cover_letter,  # XSS vulnerability - stored without sanitization
            cv_filename=cv_filename,
            cv_score=cv_score,
            additional_answers=additional_answers or {},
            status="pending"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return application


# Global instance
application_service = ApplicationService()