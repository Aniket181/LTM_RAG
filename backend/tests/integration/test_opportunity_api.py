"""
Integration Tests for Opportunity API
Tests CRUD endpoints at /api/v1/opportunities
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.api.deps import get_db

from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database for integration testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    """Clean the test database between tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_create_opportunity():
    """Test creating a new opportunity."""
    payload = {
        "name": "Test Scholarship 123",
        "provider": "Test Trust",
        "description": "A scholarship for testing",
        "opportunity_type": "Scholarship",
        "education_level": ["UG"],
        "status": "Active"
    }
    
    response = client.post("/api/v1/opportunities/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Scholarship 123"
    assert "id" in data
    
    return data["id"]


def test_get_opportunities():
    """Test retrieving list of opportunities."""
    # Create one first
    test_create_opportunity()
    
    response = client.get("/api/v1/opportunities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Scholarship 123"


def test_get_opportunity_by_id():
    """Test retrieving a specific opportunity."""
    opp_id = test_create_opportunity()
    
    response = client.get(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == opp_id


def test_update_opportunity():
    """Test updating an opportunity."""
    opp_id = test_create_opportunity()
    
    update_payload = {
        "name": "Updated Test Scholarship"
    }
    
    response = client.put(f"/api/v1/opportunities/{opp_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Scholarship"
    # Ensure other fields remain unchanged
    assert data["provider"] == "Test Trust"


def test_delete_opportunity():
    """Test deleting an opportunity."""
    opp_id = test_create_opportunity()
    
    # Delete it
    response = client.delete(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 404
