from fastapi import FastAPI
from .database import engine
from .models import models
from .routers import auth, jobs, chat, applicants
from .config import settings
from .services.data_seeder import seed_database
from .middleware.rate_limiter import rate_limit_middleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Big Kahuna Burger HR Platform",
    description="A vulnerable HR platform for educational purposes.",
    version="1.0.0",
    debug=settings.debug
)

# CORS is handled by nginx proxy to avoid duplicate headers
# Vulnerable CORS configuration is in nginx.conf

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(applicants.router)

# Startup event to seed database with mock data
@app.on_event("startup")
async def startup_event():
    """Seed database with mock data on startup if empty"""
    seed_database()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Secure global exception handler that doesn't expose sensitive information.
    """
    import logging
    
    # Log the full error for debugging (server-side only)
    logging.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    # Return generic error message to client
    return {
        "error": "An internal server error occurred",
        "type": "InternalServerError",
        "message": "Please try again later or contact support if the problem persists"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
