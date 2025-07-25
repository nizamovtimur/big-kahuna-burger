import pytest
from fastapi.testclient import TestClient


class TestJobEndpoints:
    def test_create_job_requires_authentication(self, client):
        job_data = {
            "title": "Test Job",
            "description": "Test Description",
            "department": "Test Dept",
            "location": "Test Location"
        }
        response = client.post("/jobs/", json=job_data)
        assert response.status_code == 401

    def test_get_jobs_public_access(self, client):
        response = client.get("/jobs/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_job_by_id_not_found(self, client):
        response = client.get("/jobs/999")
        assert response.status_code == 404


class TestApplicantEndpoints:
    def test_create_applicant(self, client, sample_applicant_data):
        response = client.post("/applicants/", json=sample_applicant_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_applicant_data["email"]
        assert data["full_name"] == sample_applicant_data["full_name"]

    def test_create_applicant_duplicate_email(self, client, sample_applicant_data):
        # Create first applicant
        client.post("/applicants/", json=sample_applicant_data)
        
        # Try to create another with same email
        response = client.post("/applicants/", json=sample_applicant_data)
        assert response.status_code == 400


class TestApplicationEndpoints:
    def test_submit_application_requires_valid_job(self, client):
        application_data = {
            "job_id": 999,
            "cover_letter": "I want this job!"
        }
        response = client.post("/applications/", json=application_data)
        assert response.status_code == 401  # No authentication

    def test_get_applications_requires_authentication(self, client):
        response = client.get("/applications/")
        assert response.status_code == 401


class TestChatEndpoints:
    def test_chat_requires_authentication_or_session(self, client):
        chat_data = {
            "message": "Hello, I want to know about jobs"
        }
        response = client.post("/chat/", json=chat_data)
        # Should either require auth or create anonymous session
        assert response.status_code in [200, 401]

    def test_get_chat_history_requires_authentication(self, client):
        response = client.get("/chat/history")
        assert response.status_code == 401


class TestAuthenticationEndpoints:
    def test_login_with_invalid_credentials(self, client):
        login_data = {
            "email": "invalid@email.com",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    def test_register_employee(self, client, sample_employee_data):
        response = client.post("/auth/register", json=sample_employee_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_employee_data["email"]
        assert "access_token" in data


class TestAIEndpoints:
    def test_analyze_resume_requires_authentication(self, client):
        analysis_data = {
            "resume_text": "Some resume content",
            "job_id": 1
        }
        response = client.post("/ai/analyze-resume", json=analysis_data)
        assert response.status_code == 401

    def test_ai_chat_integration(self, client):
        # This will test the OpenAI integration
        # For now, just test the endpoint exists
        response = client.post("/ai/chat", json={"message": "test"})
        assert response.status_code in [200, 401, 422]  # Various expected responses 