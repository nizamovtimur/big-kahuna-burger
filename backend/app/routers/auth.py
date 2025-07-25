from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db, execute_raw_query
from ..models.models import User
from ..schemas.schemas import UserCreate, User as UserSchema, Token
from ..services.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    WARNING: Contains XSS vulnerability in personal_notes field.
    """
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check username
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        # Vulnerable: Store personal_notes without sanitization (XSS)
        personal_notes=user.personal_notes,
        is_hr=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint with weak authentication.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_hr": current_user.is_hr,
        "personal_notes": current_user.personal_notes
    }

@router.post("/create-hr-user")
async def create_hr_user(username: str, password: str, email: str, db: Session = Depends(get_db)):
    """
    Create HR user - should be protected but isn't.
    WARNING: Anyone can create HR users!
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = get_password_hash(password)
    hr_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=f"HR User - {username}",
        is_hr=True
    )
    
    db.add(hr_user)
    db.commit()
    db.refresh(hr_user)
    
    return {"message": "HR user created successfully", "user_id": hr_user.id}

@router.get("/vulnerable-search")
async def vulnerable_user_search(search_term: str, db: Session = Depends(get_db)):
    """
    WARNING: This endpoint is intentionally vulnerable to SQL injection!
    Used for educational purposes only.
    """
    # Vulnerable: Direct string interpolation in SQL query
    query = f"SELECT username, email, full_name FROM users WHERE username LIKE '%{search_term}%' OR email LIKE '%{search_term}%'"
    
    try:
        results = execute_raw_query(query)
        return {"results": [dict(row._mapping) for row in results], "query_executed": query}
    except Exception as e:
        return {"error": str(e), "query": query}

@router.post("/vulnerable-login")
async def vulnerable_login_demo(username: str, password: str, db: Session = Depends(get_db)):
    """
    WARNING: Alternative login endpoint that's extremely vulnerable to SQL injection!
    Demonstrates authentication bypass attacks.
    """
    # EXTREMELY VULNERABLE: Direct string concatenation
    query = f"SELECT id, username, email, is_hr, full_name FROM users WHERE username = '{username}' AND hashed_password = '{password}'"
    
    try:
        results = execute_raw_query(query)
        if results:
            user_data = dict(results[0]._mapping)
            # Create a simple token (vulnerable approach)
            access_token = f"token_{user_data['username']}_{user_data['id']}"
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_data,
                "query_executed": query
            }
        else:
            return {"error": "Invalid credentials", "query_executed": query}
    except Exception as e:
        return {"error": str(e), "query": query} 