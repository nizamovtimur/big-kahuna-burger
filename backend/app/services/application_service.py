import os
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException
from ..models.models import JobApplication, Job, User


class ApplicationService:
    """
    Central service for all job application operations.
    Handles file uploads, CV analysis, and database operations.
    """
    
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upsert_application_with_score(
        self,
        db: Session,
        user: User,
        job_id: int,
        cv_filename: str,
        cv_score: int,
        cover_letter: str = "",
        additional_answers: Optional[dict] = None
    ) -> JobApplication:
        """
        Create application if absent, otherwise update CV-related fields immediately.
        Saves the CV score right away to support incremental pipelines.
        """
        # Ensure job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        existing = self.get_existing_application(db, user.id, job_id)
        if existing:
            existing.cv_filename = cv_filename
            existing.cv_score = cv_score
            if cover_letter:
                existing.cover_letter = cover_letter
            if additional_answers:
                if not existing.additional_answers:
                    existing.additional_answers = {}
                existing.additional_answers.update(additional_answers)  # unsanitized by design
                flag_modified(existing, 'additional_answers')
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create a new application record directly
            application = JobApplication(
                user_id=user.id,
                job_id=job_id,
                cover_letter=cover_letter,
                cv_filename=cv_filename,
                cv_score=cv_score,
                additional_answers=additional_answers or {},
                status="pending",
            )
            db.add(application)
            db.commit()
            db.refresh(application)
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

# Global instance
application_service = ApplicationService()
