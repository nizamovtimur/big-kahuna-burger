import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import JobApplication, Job, User
from ..schemas.schemas import JobApplicationCreate, JobApplication as JobApplicationSchema
from ..services.auth import get_current_user, get_current_hr_user
from ..services.openai_service import openai_service

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=JobApplicationSchema)
async def submit_application(
    job_id: int = Form(...),
    cover_letter: str = Form(...),
    additional_answers: str = Form(None),
    cv_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit job application with CV upload.
    WARNING: Contains multiple vulnerabilities:
    1. XSS in cover_letter and additional_answers
    2. Indirect prompt injection through PDF content (affects CV scoring)
    3. Unrestricted file upload
    """
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user already applied
    existing_app = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == job_id
    ).first()
    if existing_app:
        raise HTTPException(status_code=400, detail="Already applied to this job")
    
    # Save uploaded file (vulnerable - no validation!)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{current_user.id}_{job_id}_{cv_file.filename}")
    
    # Vulnerable: No file type validation, size limits, or malware scanning
    with open(file_path, "wb") as buffer:
        content = await cv_file.read()
        buffer.write(content)
    
    # Extract text from PDF (vulnerable to malicious content)
    cv_text = openai_service.extract_text_from_pdf(content)
    
    # Analyze CV with AI (indirect prompt injection vulnerability!)
    cv_score = await openai_service.analyze_cv(cv_text, job.description)
    
    # Parse additional answers (XSS vulnerability)
    additional_data = {}
    if additional_answers:
        try:
            # Vulnerable: Eval-like parsing without validation
            import json
            additional_data = json.loads(additional_answers)
        except:
            additional_data = {"raw_input": additional_answers}
    
    # Create application
    application = JobApplication(
        user_id=current_user.id,
        job_id=job_id,
        cover_letter=cover_letter,  # XSS vulnerability
        cv_filename=cv_file.filename,
        cv_score=cv_score,  # CV score from AI analysis (0-10)
        additional_answers=additional_data,  # XSS vulnerability
        status="pending"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application

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

@router.get("/{application_id}", response_model=JobApplicationSchema)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific application.
    WARNING: Returns unsanitized content and CV scores from potentially manipulated analysis.
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Vulnerable: No proper authorization check
    if not current_user.is_hr and application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return application

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

@router.post("/{application_id}/reanalyze")
async def reanalyze_cv(
    application_id: int,
    custom_prompt: str = None,
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    Re-analyze CV with custom prompt.
    WARNING: Allows custom prompts (severe prompt injection vulnerability!).
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Load CV content
    file_path = os.path.join("uploads", application.cv_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CV file not found")
    
    with open(file_path, "rb") as f:
        cv_content = f.read()
    
    cv_text = openai_service.extract_text_from_pdf(cv_content)
    
    # Vulnerable: Use custom prompt directly
    if custom_prompt:
        # Extremely vulnerable: Custom prompt injection
        malicious_analysis = f"""
        {custom_prompt}
        
        CV Content:
        {cv_text}
        
        Please provide a score from 0 to 10. Start your response with "Score: X/10".
        """
        
        try:
            response = await openai_service.client.chat.completions.create(
                model=openai_service.model,
                messages=[
                    {"role": "system", "content": "You are an AI analyzing a CV. Always start your response with 'Score: X/10'."},
                    {"role": "user", "content": malicious_analysis}
                ],
                max_tokens=400
            )
            ai_response = response.choices[0].message.content
            
            # Extract score using regex (vulnerable to manipulation)
            import re
            score_match = re.search(r'[Ss]core:\s*(\d+)(?:/10)?', ai_response)
            if score_match:
                new_score = int(score_match.group(1))
                new_score = min(max(new_score, 0), 10)
            else:
                # Fallback: try to find any number
                number_match = re.search(r'(\d+)', ai_response)
                if number_match:
                    new_score = int(number_match.group(1))
                    new_score = min(max(new_score, 0), 10)
                else:
                    new_score = 0
                    
        except Exception as e:
            new_score = 0
    else:
        # Use standard analysis (still vulnerable)
        job = db.query(Job).filter(Job.id == application.job_id).first()
        new_score = await openai_service.analyze_cv(cv_text, job.description)
    
    # Update application
    application.cv_score = new_score
    db.commit()
    
    return {
        "message": "CV re-analyzed",
        "new_score": new_score,
        "custom_prompt_used": custom_prompt is not None
    }

@router.post("/bulk-process")
async def bulk_process_applications(
    action: str,
    application_ids: List[int],
    custom_data: dict = None,
    current_user: User = Depends(get_current_hr_user),
    db: Session = Depends(get_db)
):
    """
    Bulk process applications.
    WARNING: Vulnerable to mass assignment and injection attacks.
    """
    processed = []
    
    for app_id in application_ids:
        application = db.query(JobApplication).filter(
            JobApplication.id == app_id
        ).first()
        
        if application:
            if action == "approve":
                application.status = "approved"
            elif action == "reject":
                application.status = "rejected"
            elif action == "custom":
                # Vulnerable: Apply custom data without validation
                if custom_data:
                    for key, value in custom_data.items():
                        if hasattr(application, key):
                            setattr(application, key, value)
            
            processed.append(app_id)
    
    db.commit()
    
    return {
        "processed_applications": processed,
        "action": action,
        "custom_data": custom_data
    } 