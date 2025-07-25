import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .database import engine, Base
from .routers import auth, jobs, applicants, chat
from .config import settings, is_production, get_openai_config
from .services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Log OpenAI configuration
    openai_info = OpenAIService.get_client_info()
    logger.info(f"OpenAI Configuration: {openai_info['base_url']} | Model: {openai_info['model']}")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive HR platform for managing job postings, applications, and AI-powered candidate interactions.",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    # Hide docs in production unless explicitly enabled
    docs_url="/docs" if not is_production() else None,
    redoc_url="/redoc" if not is_production() else None,
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security middleware
if is_production():
    # Trusted host middleware for production
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["bigkahunaburger.com", "*.bigkahunaburger.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests"""
    start_time = request.state.start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applicants.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if not is_production() else "Contact administrator for API documentation"
    }


@app.get("/health", tags=["Health"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/info", tags=["Info"])
@limiter.limit("10/minute")
async def info(request: Request):
    """System information endpoint"""
    openai_info = OpenAIService.get_client_info()
    
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "openai": {
            "base_url": openai_info["base_url"],
            "model": openai_info["model"],
            "max_tokens": openai_info["max_tokens"],
            "temperature": openai_info["temperature"]
        } if not is_production() else {"configured": True},
        "cors_origins": settings.cors_origins if not is_production() else ["configured"]
    } 