from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db, execute_raw_query
from ..models.models import Job, User
from ..schemas.schemas import JobCreate, Job as JobSchema, SearchRequest
from ..services.auth import get_current_user, get_current_hr_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/")
async def get_jobs(skip: int = 0, limit: int = 100, order_by: str = "created_at", db: Session = Depends(get_db)):
    """Get all active jobs - vulnerable to SQL injection through order_by parameter"""
    try:
        # Vulnerable: Direct string interpolation for ORDER BY clause
        query = f"SELECT * FROM jobs WHERE is_active = true ORDER BY {order_by} DESC LIMIT {limit} OFFSET {skip}"
        results = execute_raw_query(query)
        
        # Process jobs data and handle date serialization
        jobs = []
        for row in results:
            job_data = dict(row._mapping)
            # Ensure proper data types for frontend
            if job_data.get('created_at'):
                job_data['created_at'] = job_data['created_at'].isoformat()
            if job_data.get('updated_at'):
                job_data['updated_at'] = job_data['updated_at'].isoformat()
            jobs.append(job_data)
            
        return {"jobs": jobs, "query_executed": query}
    except Exception as e:
        print(f"Error in get_jobs endpoint: {str(e)}")
        return {"error": str(e), "query": query, "jobs": []}

@router.get("/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID - vulnerable to SQL injection if job_id is manipulated"""
    try:
        # Vulnerable: Direct string interpolation in SQL query
        query = f"SELECT * FROM jobs WHERE id = {job_id} AND is_active = true"
        results = execute_raw_query(query)
        
        if not results:
            raise HTTPException(status_code=404, detail="Job not found")
            
        job_data = dict(results[0]._mapping)
        
        # Ensure proper data types for frontend
        if job_data.get('created_at'):
            job_data['created_at'] = job_data['created_at'].isoformat()
        if job_data.get('updated_at'):
            job_data['updated_at'] = job_data['updated_at'].isoformat()
            
        return job_data
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_job endpoint: {str(e)}")
        print(f"Query executed: {query}")
        print(f"Job ID: {job_id}")
        # Return error details for vulnerability demonstration
        raise HTTPException(status_code=400, detail={
            "error": str(e), 
            "query": query,
            "job_id": job_id
        })

@router.post("/", response_model=JobSchema)
async def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
):
    """
    Create a new job posting.
    WARNING: Stores raw HTML content without sanitization (XSS vulnerability).
    """
    db_job = Job(
        title=job.title,
        # Vulnerable: Raw HTML stored without sanitization
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        additional_info=job.additional_info,
        created_by=current_user.id
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.put("/{job_id}", response_model=JobSchema)
async def update_job(
    job_id: int,
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
):
    """
    Update a job posting.
    WARNING: Updates without proper sanitization (XSS vulnerability).
    """
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Vulnerable: Direct assignment without sanitization
    db_job.title = job.title
    db_job.description = job.description
    db_job.requirements = job.requirements
    db_job.location = job.location
    db_job.salary_range = job.salary_range
    db_job.additional_info = job.additional_info
    
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
):
    """Deactivate a job posting"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db_job.is_active = False
    db.commit()
    
    return {"message": "Job deactivated successfully"}

@router.post("/search")
async def vulnerable_job_search(request: SearchRequest, db: Session = Depends(get_db)):
    """
    WARNING: This endpoint is intentionally vulnerable to SQL injection!
    Used for educational purposes to demonstrate SQL injection attacks.
    """
    search_term = request.search_term
    
    # Vulnerable: Direct string interpolation in SQL query
    base_query = f"""
        SELECT id, title, description, requirements, location, salary_range, additional_info, created_at
        FROM jobs 
        WHERE is_active = true 
        AND (title LIKE '%{search_term}%' 
             OR description LIKE '%{search_term}%' 
             OR location LIKE '%{search_term}%')
    """
    
    # Add filters if provided (also vulnerable)
    if request.filters:
        for key, value in request.filters.items():
            base_query += f" AND {key} LIKE '%{value}%'"
    
    try:
        results = execute_raw_query(base_query)
        return {
            "results": [dict(row._mapping) for row in results],
            "query": base_query  # Exposing query for educational purposes
        }
    except Exception as e:
        return {
            "error": str(e),
            "query": base_query,
            "message": "SQL query failed - check for injection attempts"
        }

@router.get("/by-location/{location}")
async def get_jobs_by_location_vulnerable(location: str, db: Session = Depends(get_db)):
    """
    WARNING: Vulnerable to SQL injection through location parameter.
    """
    # Vulnerable: Direct string interpolation
    query = f"SELECT * FROM jobs WHERE location = '{location}' AND is_active = true"
    
    try:
        results = execute_raw_query(query)
        return {"jobs": [dict(row._mapping) for row in results], "query_executed": query}
    except Exception as e:
        return {"error": str(e), "query": query}

@router.post("/bulk-update")
async def bulk_update_jobs(
    job_ids: List[int],
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
):
    """
    Bulk update jobs with vulnerable implementation.
    WARNING: Allows arbitrary field updates without validation.
    """
    updated_jobs = []
    
    for job_id in job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            # Vulnerable: Apply updates without validation
            for field, value in updates.items():
                if hasattr(job, field):
                    setattr(job, field, value)
            updated_jobs.append(job.id)
    
    db.commit()
    
    return {
        "message": f"Updated {len(updated_jobs)} jobs",
        "updated_job_ids": updated_jobs
    }

@router.get("/admin/stats")
async def get_job_statistics(
    user_role: str = "candidate", 
    min_salary: str = "0",
    db: Session = Depends(get_db)
):
    """
    WARNING: Administrative endpoint with multiple SQL injection vulnerabilities!
    Demonstrates UNION-based, Boolean-based, and error-based SQL injection.
    """
    try:
        # Multiple vulnerable parameters
        base_query = f"""
        SELECT 
            COUNT(*) as total_jobs,
            AVG(CAST(SUBSTRING(salary_range FROM '[0-9]+') AS INTEGER)) as avg_salary,
            location,
            title
        FROM jobs 
        WHERE is_active = true 
        AND salary_range LIKE '%{min_salary}%'
        """
        
        # Additional vulnerable filter based on user role
        if user_role == "hr":
            query = base_query + f" AND created_by IN (SELECT id FROM users WHERE is_hr = true)"
        else:
            query = base_query + f" AND title LIKE '%{user_role}%'"
            
        query += " GROUP BY location, title ORDER BY total_jobs DESC"
        
        results = execute_raw_query(query)
        return {
            "statistics": [dict(row._mapping) for row in results],
            "query_executed": query,
            "parameters": {
                "user_role": user_role,
                "min_salary": min_salary
            }
        }
    except Exception as e:
        return {
            "error": str(e), 
            "query": query,
            "hint": "Try UNION SELECT or boolean-based injection techniques"
        } 