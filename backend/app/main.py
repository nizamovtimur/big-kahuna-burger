from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import models
from .routers import auth, jobs, chat, applicants
from .config import settings
from .services.data_seeder import seed_database

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Big Kahuna Burger HR Platform",
    description="A vulnerable HR platform for educational purposes. Uses raw SQL execution to demonstrate real SQL injection vulnerabilities.",
    version="1.0.0",
    debug=settings.debug
)

# CORS is handled by nginx proxy to avoid duplicate headers
# Vulnerable CORS configuration is in nginx.conf

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(applicants.router, prefix="/api")

# Startup event to seed database with mock data
@app.on_event("startup")
async def startup_event():
    """Seed database with mock data on startup if empty"""
    seed_database()

@app.get("/")
async def root():
    """Welcome page with vulnerability information"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Big Kahuna Burger HR Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
            .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .warning { background-color: #ff6b6b; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .feature { background-color: #4ecdc4; color: white; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .vulnerability { background-color: #feca57; color: #2f3542; padding: 10px; margin: 5px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍔 Big Kahuna Burger HR Platform</h1>
            
            <div class="warning">
                <h2>⚠️ WARNING - EDUCATIONAL PURPOSES ONLY</h2>
                <p>This application contains intentional security vulnerabilities for educational purposes. 
                DO NOT use in production or with real data!</p>
            </div>
            
            <h2>🎯 Features</h2>
            <div class="feature">✅ AI-powered job matching and chat</div>
            <div class="feature">✅ PDF CV analysis and storage</div>
            <div class="feature">✅ HR dashboard for application management</div>
            <div class="feature">✅ User registration and authentication</div>
            
            <h2>🔴 Intentional Vulnerabilities</h2>
            <div class="vulnerability">🚨 Prompt Injection in AI Chat (RAG)</div>
            <div class="vulnerability">🚨 Indirect Prompt Injection in PDF Processing</div>
            <div class="vulnerability">🚨 Cross-Site Scripting (XSS)</div>
            <div class="vulnerability">🚨 SQL Injection</div>
            <div class="vulnerability">🚨 Insecure File Upload</div>
            <div class="vulnerability">🚨 Weak Authentication</div>
            <div class="vulnerability">🚨 Permissive CORS</div>
            <div class="vulnerability">🚨 Information Disclosure</div>
            
            <h2>🔗 API Documentation</h2>
            <p><a href="/docs" target="_blank">Interactive API Documentation (Swagger UI)</a></p>
            <p><a href="/redoc" target="_blank">Alternative API Documentation (ReDoc)</a></p>
            
            <h2>🎯 Interfaces</h2>
            <p><strong>Candidate Interface:</strong> Chat with AI, browse jobs, submit applications</p>
            <p><strong>HR Interface:</strong> Manage jobs, review applications, analyze CVs</p>
            
            <h2>🔧 Getting Started</h2>
            <ol>
                <li>The backend automatically creates mock data when it starts</li>
                <li>Login with test accounts (hr_admin/secret123 or candidate1/secret123)</li>
                <li>Explore job postings and applications</li>
                <li>Test vulnerabilities with provided examples</li>
                <li>Use the AI chat system to try prompt injection attacks</li>
            </ol>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Big Kahuna Burger HR Platform is running"}

@app.get("/api/debug/config")
async def debug_config():
    """
    WARNING: Exposes configuration for debugging (vulnerability!)
    """
    return {
        "openai_model": settings.openai_model,
        "openai_base_url": settings.openai_base_url,
        "database_url": settings.database_url,  # Vulnerable: Exposes DB credentials
        "secret_key": settings.secret_key,      # Vulnerable: Exposes secret key
        "debug": settings.debug,
        "environment": settings.environment,
        "warning": "This endpoint should never exist in production!"
    }

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