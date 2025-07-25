from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import Applicant as ApplicantModel, Application as ApplicationModel, Job as JobModel
from ..schemas.schemas import Applicant, ApplicantCreate, Application, ApplicationCreate, ApplicationUpdate
from ..routers.auth import get_current_user
from ..services.openai_service import OpenAIService

router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.post("/", response_model=Applicant, status_code=status.HTTP_201_CREATED)
async def create_applicant(
    applicant_data: ApplicantCreate,
    db: Session = Depends(get_db)
):
    # Check if applicant already exists
    existing_applicant = db.query(ApplicantModel).filter(
        ApplicantModel.email == applicant_data.email
    ).first()
    
    if existing_applicant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant with this email already exists"
        )
    
    applicant = ApplicantModel(**applicant_data.dict())
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant


@router.get("/", response_model=List[Applicant])
async def get_applicants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    applicants = db.query(ApplicantModel).offset(skip).limit(limit).all()
    return applicants


@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(
    applicant_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    applicant = db.query(ApplicantModel).filter(ApplicantModel.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant


@router.post("/{applicant_id}/apply", response_model=Application, status_code=status.HTTP_201_CREATED)
async def submit_application(
    applicant_id: int,
    application_data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    # Verify applicant exists
    applicant = db.query(ApplicantModel).filter(ApplicantModel.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    # Verify job exists
    job = db.query(JobModel).filter(JobModel.id == application_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if application already exists
    existing_application = db.query(ApplicationModel).filter(
        ApplicationModel.applicant_id == applicant_id,
        ApplicationModel.job_id == application_data.job_id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application for this job already exists"
        )
    
    # Create application
    application = ApplicationModel(
        applicant_id=applicant_id,
        **application_data.dict()
    )
    
    # Analyze resume if available
    if applicant.resume_text and job.description:
        try:
            analysis = OpenAIService.analyze_resume_match(
                applicant.resume_text,
                job.description,
                job.requirements or ""
            )
            application.ai_match_score = analysis.get("score", 0)
            application.ai_analysis = analysis.get("summary", "Analysis completed")
        except Exception as e:
            # Continue without AI analysis if it fails
            application.ai_analysis = f"AI analysis failed: {str(e)}"
    
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{applicant_id}/applications", response_model=List[Application])
async def get_applicant_applications(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    applications = db.query(ApplicationModel).filter(
        ApplicationModel.applicant_id == applicant_id
    ).all()
    return applications


@router.put("/applications/{application_id}", response_model=Application)
async def update_application_status(
    application_id: int,
    application_update: ApplicationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = db.query(ApplicationModel).filter(
        ApplicationModel.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = application_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application 