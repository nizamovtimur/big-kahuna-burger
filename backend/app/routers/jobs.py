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





 