from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import Job as JobModel, Employee
from ..schemas.schemas import Job, JobCreate, JobUpdate
from ..routers.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[Job])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(JobModel).filter(JobModel.is_active == True)
    
    if department:
        query = query.filter(JobModel.department.ilike(f"%{department}%"))
    if location:
        query = query.filter(JobModel.location.ilike(f"%{location}%"))
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id, JobModel.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = JobModel(**job_data.dict(), created_by_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user is the creator or has admin rights
    if job.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user is the creator or has admin rights
    if job.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    # Soft delete by setting is_active to False
    job.is_active = False
    db.commit()
    
    return {"message": "Job deleted successfully"} 