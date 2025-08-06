from fastapi import FastAPI
from .database import engine
from .models import models
from .routers import auth, jobs, chat, applicants
from .config import settings
from .services.data_seeder import seed_database

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
    Global exception handler that exposes sensitive information
    WARNING: This is a vulnerability for educational purposes!
    """
    import traceback
    return {
        "error": str(exc),
        "type": type(exc).__name__,
        "traceback": traceback.format_exc(),  # Vulnerable: Exposes stack trace
        "request_url": str(request.url),
        "warning": "This error information should not be exposed in production!"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
