from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    department = Column(String)
    role = Column(String, default="hr")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    jobs = relationship("Job", back_populates="created_by_employee")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    location = Column(String, nullable=False)
    salary_min = Column(Float)
    salary_max = Column(Float)
    requirements = Column(Text)
    additional_questions = Column(Text)  # JSON string for custom questions
    is_active = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    created_by_employee = relationship("Employee", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Applicant(Base):
    __tablename__ = "applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    resume_text = Column(Text)
    resume_filename = Column(String)
    skills = Column(Text)  # JSON string
    experience_years = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    applications = relationship("Application", back_populates="applicant")
    chat_sessions = relationship("ChatSession", back_populates="applicant")


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    cover_letter = Column(Text)
    status = Column(String, default="submitted")  # submitted, reviewing, interview, rejected, hired
    ai_match_score = Column(Float)  # AI-calculated relevance score
    ai_analysis = Column(Text)  # AI analysis of resume vs job
    additional_info = Column(Text)  # JSON string for answers to custom questions
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    job = relationship("Job", back_populates="applications")
    applicant = relationship("Applicant", back_populates="applications")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    session_data = Column(Text)  # JSON string for chat history
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    applicant = relationship("Applicant", back_populates="chat_sessions") 