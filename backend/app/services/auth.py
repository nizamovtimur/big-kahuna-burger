from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.models import Employee
from ..schemas.schemas import TokenData
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[Employee]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
        return token_data
    except JWTError:
        return None


def create_employee(db: Session, email: str, password: str, full_name: str, 
                   department: Optional[str] = None, role: str = "hr") -> Employee:
    hashed_password = get_password_hash(password)
    db_employee = Employee(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        department=department,
        role=role
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee 