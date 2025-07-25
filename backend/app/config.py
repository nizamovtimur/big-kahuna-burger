import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = "your_openai_api_key_here"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # Database Configuration
    database_url: str = "postgresql://hr_platform:vulnerable_password_123@db:5432/big_kahuna_hr"
    
    # Security (Intentionally Weak)
    secret_key: str = "super_secret_key_that_should_be_random"
    jwt_secret_key: str = "another_weak_secret_for_jwt"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS (Intentionally Permissive)
    cors_origins: list = ["http://localhost:3000"]
    
    # Debug
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings() 