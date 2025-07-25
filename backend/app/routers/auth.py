from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.schemas import Token, UserLogin, EmployeeCreate, Employee
from ..services.auth import (
    authenticate_user, create_access_token, create_employee, 
    verify_token, get_user_by_email
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email(db, employee_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new employee
    employee = create_employee(
        db, 
        email=employee_data.email,
        password=employee_data.password,
        full_name=employee_data.full_name,
        department=employee_data.department,
        role=employee_data.role
    )
    
    # Create access token for immediate login
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": employee.email}, expires_delta=access_token_expires
    )
    
    return {
        "id": employee.id,
        "email": employee.email,
        "full_name": employee.full_name,
        "access_token": access_token,
        "token_type": "bearer"
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user


@router.get("/me", response_model=Employee)
async def read_users_me(current_user: Employee = Depends(get_current_user)):
    return current_user 