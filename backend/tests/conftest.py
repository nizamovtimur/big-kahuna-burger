import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_employee_data():
    return {
        "email": "hr@bigkahuna.com",
        "password": "testpass123",
        "full_name": "HR Manager",
        "department": "Human Resources",
        "role": "hr"
    }


@pytest.fixture
def sample_job_data():
    return {
        "title": "Burger Flipper",
        "description": "Responsible for cooking delicious burgers at Big Kahuna Burger",
        "department": "Kitchen",
        "location": "Los Angeles, CA",
        "salary_min": 35000,
        "salary_max": 45000,
        "requirements": "Previous food service experience preferred"
    }


@pytest.fixture
def sample_applicant_data():
    return {
        "email": "john.doe@email.com",
        "full_name": "John Doe",
        "phone": "+1-555-0123",
        "skills": '["cooking", "customer service", "teamwork"]',
        "experience_years": 3
    } 