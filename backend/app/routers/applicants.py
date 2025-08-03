
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, execute_raw_query
from ..models.models import JobApplication, Job, User
from ..schemas.schemas import JobApplication as JobApplicationSchema
from ..services.auth import get_current_user, get_current_hr_user


from pydantic import BaseModel

router = APIRouter(prefix="/applications", tags=["applications"])



@router.get("/", response_model=List[JobApplicationSchema])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's applications"""
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()
    return applications

@router.get("/hr")
async def get_all_applications(
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications for HR review with user and job details.
    WARNING: Returns unsanitized content (XSS vulnerability).
    """
    try:
        # Use raw SQL to get applications with related user and job data
        query = """
        SELECT 
            ja.*,
            u.username, u.email, u.full_name, u.personal_notes,
            j.title as job_title, j.location as job_location, j.description as job_description
        FROM job_applications ja
        LEFT JOIN users u ON ja.user_id = u.id
        LEFT JOIN jobs j ON ja.job_id = j.id
        ORDER BY ja.applied_at DESC
        """
        
        results = execute_raw_query(query)
        
        applications = []
        for row in results:
            row_dict = dict(row._mapping)
            
            # Serialize datetime
            if row_dict.get('applied_at'):
                row_dict['applied_at'] = row_dict['applied_at'].isoformat()
            
            # Structure the response
            application = {
                "id": row_dict['id'],
                "user_id": row_dict['user_id'],
                "job_id": row_dict['job_id'],
                "cover_letter": row_dict['cover_letter'],
                "cv_filename": row_dict['cv_filename'],
                "cv_score": row_dict['cv_score'],
                "additional_answers": row_dict['additional_answers'],
                "status": row_dict['status'],
                "applied_at": row_dict['applied_at'],
                "user": {
                    "username": row_dict['username'],
                    "email": row_dict['email'],
                    "full_name": row_dict['full_name'],
                    "personal_notes": row_dict['personal_notes']
                },
                "job": {
                    "title": row_dict['job_title'],
                    "location": row_dict['job_location'],
                    "description": row_dict['job_description']
                }
            }
            applications.append(application)
        
        return applications
        
    except Exception as e:
        print(f"Error in HR applications endpoint: {str(e)}")
        return {"error": str(e), "applications": []}



@router.put("/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    feedback: str = None,
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    Update application status.
    WARNING: Stores feedback without sanitization (XSS vulnerability).
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Vulnerable: Direct assignment without validation
    application.status = status
    
    if feedback:
        # Vulnerable: Store feedback without sanitization
        if not application.additional_answers:
            application.additional_answers = {}
        application.additional_answers["hr_feedback"] = feedback  # XSS vulnerability
    
    db.commit()
    
    return {"message": "Application status updated", "new_status": status}


 

@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    HARD DELETE application - permanently removes from database.
    WARNING: This is irreversible! Only for HR users.
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Store info for response before deletion
    deleted_info = {
        "id": application.id,
        "user_id": application.user_id,
        "job_id": application.job_id,
        "applied_at": application.applied_at.isoformat() if application.applied_at else None
    }
    
    # Delete associated files if they exist
    if application.cv_filename:
        cv_file_path = os.path.join("uploads", application.cv_filename)
        if os.path.exists(cv_file_path):
            try:
                os.remove(cv_file_path)
            except Exception as e:
                print(f"Warning: Could not delete CV file {cv_file_path}: {e}")
    
    # HARD DELETE from database
    db.delete(application)
    db.commit()
    
    return {
        "message": "Application permanently deleted",
        "deleted_application": deleted_info,
        "warning": "This action is irreversible!"
    }

# Add bulk delete request model
class BulkDeleteRequest(BaseModel):
    application_ids: List[int]
    confirm_deletion: bool = False

@router.post("/bulk-delete")
async def bulk_delete_applications(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    Bulk HARD DELETE applications.
    WARNING: This will permanently delete multiple applications!
    """
    if not request.confirm_deletion:
        raise HTTPException(
            status_code=400, 
            detail="Must confirm deletion by setting confirm_deletion=true"
        )
    
    deleted_applications = []
    deleted_files = []
    
    for app_id in request.application_ids:
        application = db.query(JobApplication).filter(
            JobApplication.id == app_id
        ).first()
        
        if application:
            # Store info before deletion
            deleted_info = {
                "id": application.id,
                "user_id": application.user_id,
                "job_id": application.job_id,
                "cv_filename": application.cv_filename
            }
            
            # Delete CV file if exists
            if application.cv_filename:
                cv_file_path = os.path.join("uploads", application.cv_filename)
                if os.path.exists(cv_file_path):
                    try:
                        os.remove(cv_file_path)
                        deleted_files.append(application.cv_filename)
                    except Exception as e:
                        print(f"Warning: Could not delete CV file {cv_file_path}: {e}")
            
            # Delete from database
            db.delete(application)
            deleted_applications.append(deleted_info)
    
    db.commit()
    
    return {
        "message": f"Permanently deleted {len(deleted_applications)} applications",
        "deleted_applications": deleted_applications,
        "deleted_files": deleted_files,
        "warning": "This action is irreversible!"
    } 

@router.get("/check/{job_id}")
async def check_application_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user has already applied to this job.
    Returns application status or null if not applied.
    """
    application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == job_id
    ).first()
    
    if application:
        return {
            "has_applied": True,
            "application_id": application.id,
            "status": application.status,
            "applied_at": application.applied_at.isoformat() if application.applied_at else None
        }
    else:
        return {
            "has_applied": False,
            "application_id": None,
            "status": None,
            "applied_at": None
        } 