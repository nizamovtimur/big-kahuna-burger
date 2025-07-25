import pytest
from app.models.models import Employee, Job, Applicant, Application, ChatSession


class TestEmployeeModel:
    def test_create_employee(self, db_session):
        employee = Employee(
            email="test@bigkahuna.com",
            hashed_password="hashedpass123",
            full_name="Test Employee",
            department="HR",
            role="hr"
        )
        db_session.add(employee)
        db_session.commit()
        
        assert employee.id is not None
        assert employee.email == "test@bigkahuna.com"
        assert employee.is_active is True
        assert employee.created_at is not None


class TestJobModel:
    def test_create_job(self, db_session):
        # First create an employee
        employee = Employee(
            email="hr@bigkahuna.com",
            hashed_password="hashedpass",
            full_name="HR Manager"
        )
        db_session.add(employee)
        db_session.commit()
        
        job = Job(
            title="Software Engineer",
            description="Develop awesome applications",
            department="Engineering",
            location="San Francisco, CA",
            salary_min=80000,
            salary_max=120000,
            created_by_id=employee.id
        )
        db_session.add(job)
        db_session.commit()
        
        assert job.id is not None
        assert job.title == "Software Engineer"
        assert job.is_active is True
        assert job.created_by_id == employee.id


class TestApplicantModel:
    def test_create_applicant(self, db_session):
        applicant = Applicant(
            email="candidate@email.com",
            full_name="Jane Candidate",
            phone="+1-555-0123",
            skills='["python", "javascript"]',
            experience_years=5
        )
        db_session.add(applicant)
        db_session.commit()
        
        assert applicant.id is not None
        assert applicant.email == "candidate@email.com"
        assert applicant.experience_years == 5


class TestApplicationModel:
    def test_create_application(self, db_session):
        # Create employee
        employee = Employee(
            email="hr@bigkahuna.com",
            hashed_password="hashedpass",
            full_name="HR Manager"
        )
        db_session.add(employee)
        db_session.commit()
        
        # Create job
        job = Job(
            title="Developer",
            description="Code stuff",
            department="Engineering",
            location="Remote",
            created_by_id=employee.id
        )
        db_session.add(job)
        db_session.commit()
        
        # Create applicant
        applicant = Applicant(
            email="dev@email.com",
            full_name="Dev Candidate"
        )
        db_session.add(applicant)
        db_session.commit()
        
        # Create application
        application = Application(
            job_id=job.id,
            applicant_id=applicant.id,
            cover_letter="I want this job!",
            status="submitted"
        )
        db_session.add(application)
        db_session.commit()
        
        assert application.id is not None
        assert application.status == "submitted"
        assert application.job_id == job.id
        assert application.applicant_id == applicant.id


class TestChatSessionModel:
    def test_create_chat_session(self, db_session):
        # Create applicant
        applicant = Applicant(
            email="chat@email.com",
            full_name="Chat User"
        )
        db_session.add(applicant)
        db_session.commit()
        
        chat_session = ChatSession(
            applicant_id=applicant.id,
            session_data='{"messages": [{"role": "user", "content": "Hello"}]}'
        )
        db_session.add(chat_session)
        db_session.commit()
        
        assert chat_session.id is not None
        assert chat_session.applicant_id == applicant.id
        assert '"Hello"' in chat_session.session_data 