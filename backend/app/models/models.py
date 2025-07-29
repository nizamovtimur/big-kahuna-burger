from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_hr = Column(Boolean, default=False)
    # Vulnerable: Storing sensitive data without proper encryption
    personal_notes = Column(Text)  # XSS vulnerability
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    applications = relationship("JobApplication", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)  # XSS vulnerability
    requirements = Column(Text)  # XSS vulnerability
    location = Column(String)
    salary_range = Column(String)
    is_active = Column(Boolean, default=True)
    # Vulnerable: Raw HTML content stored without sanitization
    additional_info = Column(Text)  # XSS vulnerability
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    applications = relationship("JobApplication", back_populates="job")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    # Vulnerable: Raw user input stored without sanitization
    cover_letter = Column(Text)  # XSS vulnerability
    cv_filename = Column(String)
    cv_score = Column(Integer)  # CV score 0-10 from AI analysis
    additional_answers = Column(JSON)  # XSS vulnerability in JSON values
    status = Column(String, default="pending")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    title = Column(String, nullable=True)  # Optional session title
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    # Vulnerable: Messages stored without sanitization
    content = Column(Text)  # XSS and prompt injection vulnerability
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("ChatSession", back_populates="messages")

class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    # Vulnerable: System prompts can be modified through user input
    content = Column(Text)  # Prompt injection vulnerability
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 