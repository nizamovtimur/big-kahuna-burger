from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    personal_notes: Optional[str] = None  # XSS vulnerability

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_hr: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Job Schemas
class JobBase(BaseModel):
    title: str
    description: str  # XSS vulnerability
    requirements: str  # XSS vulnerability
    location: str
    salary_range: Optional[str] = None
    additional_info: Optional[str] = None  # XSS vulnerability

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True

# Application Schemas
class JobApplicationBase(BaseModel):
    cover_letter: str  # XSS vulnerability
    additional_answers: Optional[Dict[str, Any]] = None  # XSS vulnerability

class JobApplicationCreate(JobApplicationBase):
    job_id: int

class JobApplication(JobApplicationBase):
    id: int
    user_id: int
    job_id: int
    cv_filename: Optional[str] = None
    cv_score: Optional[int] = None  # CV score 0-10 from AI analysis
    status: str
    applied_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    message: str  # Prompt injection vulnerability
    job_id: Optional[int] = None

class ChatResponse(BaseModel):
    user_message: str
    ai_response: str  # Potential for malicious content
    created_at: datetime

# Vulnerable Schemas for Raw Queries
class RawQueryRequest(BaseModel):
    """WARNING: This schema is intentionally vulnerable to SQL injection"""
    query: str  # SQL injection vulnerability
    
class SearchRequest(BaseModel):
    """WARNING: This schema allows unsanitized search terms"""
    search_term: str  # XSS vulnerability
    filters: Optional[Dict[str, str]] = None  # Additional XSS vulnerability

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 