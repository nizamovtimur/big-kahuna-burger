from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Employee schemas
class EmployeeBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = None
    role: str = "hr"


class EmployeeCreate(EmployeeBase):
    password: str


class Employee(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job schemas
class JobBase(BaseModel):
    title: str
    description: str
    department: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    additional_questions: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    additional_questions: Optional[str] = None
    is_active: Optional[bool] = None


class Job(JobBase):
    id: int
    is_active: bool
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Applicant schemas
class ApplicantBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None


class ApplicantCreate(ApplicantBase):
    resume_text: Optional[str] = None
    resume_filename: Optional[str] = None


class Applicant(ApplicantBase):
    id: int
    resume_text: Optional[str] = None
    resume_filename: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Application schemas
class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    additional_info: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    job_id: int


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    ai_match_score: Optional[float] = None
    ai_analysis: Optional[str] = None


class Application(ApplicationBase):
    id: int
    job_id: int
    applicant_id: int
    status: str
    ai_match_score: Optional[float] = None
    ai_analysis: Optional[str] = None
    submitted_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatSessionCreate(BaseModel):
    job_id: Optional[int] = None
    message: str


class ChatSessionResponse(BaseModel):
    message: str
    session_id: int


class ChatSession(BaseModel):
    id: int
    applicant_id: int
    job_id: Optional[int] = None
    session_data: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str 