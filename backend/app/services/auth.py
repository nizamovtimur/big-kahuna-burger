from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from ..config import settings
from ..models.models import User
from ..database import get_db
from ..schemas.schemas import TokenData

# Intentionally weak password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """Verify password with weak security"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password with weak security"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with vulnerable implementation"""
    # Vulnerable: Direct SQL injection in authentication
    from ..database import execute_raw_query
    
    try:
        # EXTREMELY VULNERABLE: Direct string concatenation in SQL
        query = f"SELECT id, username, email, hashed_password, full_name, is_hr FROM users WHERE username = '{username}'"
        results = execute_raw_query(query)
        
        if not results:
            return False
            
        user_data = dict(results[0]._mapping)
        
        # Verify password
        if not verify_password(password, user_data['hashed_password']):
            return False
            
        # Return a user-like object
        class UserResult:
            def __init__(self, data):
                self.id = data['id']
                self.username = data['username']
                self.email = data['email']
                self.hashed_password = data['hashed_password']
                self.full_name = data['full_name']
                self.is_hr = data['is_hr']
        
        return UserResult(user_data)
        
    except Exception as e:
        # Return False on any SQL error (could be injection attempt)
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token with weak secret"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Vulnerable: Weak secret key
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get current user with vulnerable token validation"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Vulnerable: Weak secret key used for verification
        payload = jwt.decode(token.credentials, settings.jwt_secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_hr_user(current_user: User = Depends(get_current_user)):
    """Get current HR user with basic role check"""
    if not current_user.is_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user 