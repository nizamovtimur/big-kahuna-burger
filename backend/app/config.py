import os
import secrets
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # =================================================================
    # APPLICATION SETTINGS
    # =================================================================
    app_name: str = "Big Kahuna Burger HR Platform"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # =================================================================
    # SECURITY SETTINGS
    # =================================================================
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1000"))
    
    # Password requirements
    min_password_length: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    require_special_chars: bool = os.getenv("REQUIRE_SPECIAL_CHARS", "true").lower() == "true"
    
    # SSL/Security
    ssl_required: bool = os.getenv("SSL_REQUIRED", "false").lower() == "true"
    secure_cookies: bool = os.getenv("SECURE_COOKIES", "false").lower() == "true"
    
    # =================================================================
    # DATABASE CONFIGURATION
    # =================================================================
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/bigkahuna_hr"
    )
    
    # Database pool settings
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # =================================================================
    # OPENAI CONFIGURATION
    # =================================================================
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    openai_timeout: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
    openai_max_retries: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    
    # =================================================================
    # CORS CONFIGURATION
    # =================================================================
    cors_origins: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
        if origin.strip()
    ]
    
    # =================================================================
    # RATE LIMITING
    # =================================================================
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    rate_limit_burst: int = int(os.getenv("RATE_LIMIT_BURST", "100"))
    
    # =================================================================
    # FILE UPLOAD SETTINGS
    # =================================================================
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    allowed_file_types: List[str] = [
        ext.strip() 
        for ext in os.getenv("ALLOWED_FILE_TYPES", "pdf,doc,docx,txt").split(",")
        if ext.strip()
    ]
    
    # =================================================================
    # EMAIL CONFIGURATION
    # =================================================================
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_from_email: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    
    # =================================================================
    # CLOUD STORAGE (AWS S3)
    # =================================================================
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: Optional[str] = os.getenv("AWS_S3_BUCKET")
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    
    # =================================================================
    # REDIS CONFIGURATION
    # =================================================================
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # =================================================================
    # MONITORING & LOGGING
    # =================================================================
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # =================================================================
    # VALIDATION
    # =================================================================
    def validate_settings(self):
        """Validate critical settings"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Validate OpenAI base URL format
        if not self.openai_base_url.startswith(('http://', 'https://')):
            raise ValueError("OPENAI_BASE_URL must be a valid URL starting with http:// or https://")
        
        if self.environment == "production":
            if self.secret_key == "your-secret-key-here":
                raise ValueError("SECRET_KEY must be changed in production")
            
            if not self.ssl_required:
                print("WARNING: SSL not required in production environment")
        
        if len(self.secret_key) < 32:
            print("WARNING: SECRET_KEY should be at least 32 characters long")
            
        # Log OpenAI configuration (without exposing API key)
        print(f"OpenAI Configuration:")
        print(f"  - Base URL: {self.openai_base_url}")
        print(f"  - Model: {self.openai_model}")
        print(f"  - Max Tokens: {self.openai_max_tokens}")
        print(f"  - Temperature: {self.openai_temperature}")
        print(f"  - Timeout: {self.openai_timeout}s")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Validate settings on import
try:
    settings.validate_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    if settings.environment == "production":
        raise
    else:
        print("Continuing with development defaults...")


# Helper functions for common operations
def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() == "development"


def get_database_url() -> str:
    """Get database URL with pool settings"""
    return settings.database_url


def get_cors_origins() -> List[str]:
    """Get CORS origins list"""
    return settings.cors_origins


def get_openai_config() -> dict:
    """Get OpenAI configuration dictionary"""
    return {
        "api_key": settings.openai_api_key,
        "base_url": settings.openai_base_url,
        "model": settings.openai_model,
        "max_tokens": settings.openai_max_tokens,
        "temperature": settings.openai_temperature,
        "timeout": settings.openai_timeout,
        "max_retries": settings.openai_max_retries
    } 