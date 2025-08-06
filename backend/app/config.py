from os import getenv
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    openai_base_url: str = getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # Database Configuration
    database_url: str = getenv("DATABASE_URL", "postgresql://big_kahuna_hr:vulnerable_password_123@db:5432/big_kahuna_hr")
    
    # Security (Intentionally Weak)
    secret_key: str = getenv("SECRET_KEY", "super_secret_key_that_should_be_random")
    jwt_secret_key: str = getenv("JWT_SECRET_KEY", "another_weak_secret_for_jwt")
    algorithm: str = getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Debug
    environment: str = getenv("ENVIRONMENT", "development")
    debug: bool = getenv("DEBUG", "True") == "True"

    class Config:
        env_file = ".env"

settings = Settings() 