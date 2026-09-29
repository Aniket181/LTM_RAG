"""
Integration Tests for Students API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.core.config import settings

engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def real_db_engine():
    yield engine

@pytest.fixture
def db_session(real_db_engine):
    connection = real_db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def override_db(db_session):
    def _override():
        yield db_session
    
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_db):
    return TestClient(app)


def _create_dummy_student(client: TestClient) -> str:
    """Helper to create a student and return their ID."""
    payload = {
        "name": "Test Student 1",
        "education_level": "UG",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year_of_study": 3,
        "cgpa": 8.5,
        "annual_family_income": 500000.0,
        "category": "General",
        "gender": "Male",
        "state": "Maharashtra"
    }
    response = client.post("/api/v1/students/", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def test_create_student(client: TestClient):
    """Test creating a new student profile."""
    payload = {
        "name": "Test Student 2",
        "education_level": "PG",
        "course": "M.Tech",
        "category": "OBC",
        "gender": "Female"
    }
    response = client.post("/api/v1/students/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Student 2"
    assert data["course"] == "M.Tech"
    assert "id" in data


def test_get_students(client: TestClient):
    """Test retrieving list of students."""
    student_id = _create_dummy_student(client)
    
    response = client.get("/api/v1/students/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    matching_students = [s for s in data if s["id"] == student_id]
    assert len(matching_students) == 1
    assert matching_students[0]["name"] == "Test Student 1"


def test_get_student_by_id(client: TestClient):
    """Test retrieving a specific student."""
    student_id = _create_dummy_student(client)
    
    response = client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id
    assert data["cgpa"] == 8.5


def test_update_student(client: TestClient):
    """Test updating a student profile."""
    student_id = _create_dummy_student(client)
    
    update_payload = {
        "cgpa": 9.2,
        "category": "EWS"
    }
    response = client.put(f"/api/v1/students/{student_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cgpa"] == 9.2
    assert data["category"] == "EWS"
    # Ensure other fields are unchanged
    assert data["name"] == "Test Student 1"


def test_delete_student(client: TestClient):
    """Test deleting a student profile."""
    student_id = _create_dummy_student(client)
    
    response = client.delete(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 404
