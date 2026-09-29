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

from app.core.config import settings

# Connect to the real PostgreSQL database
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


def _create_dummy_opportunity(client):
    """Helper to create an opportunity and return its ID."""
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
    return response.json()["id"]


def test_create_opportunity(client):
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


def test_get_opportunities(client):
    """Test retrieving list of opportunities."""
    # Create one first
    opp_id = _create_dummy_opportunity(client)
    
    response = client.get("/api/v1/opportunities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    matching_opps = [opp for opp in data if opp["id"] == opp_id]
    assert len(matching_opps) == 1
    assert matching_opps[0]["name"] == "Test Scholarship 123"


def test_get_opportunity_by_id(client):
    """Test retrieving a specific opportunity."""
    opp_id = _create_dummy_opportunity(client)
    
    response = client.get(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == opp_id


def test_update_opportunity(client):
    """Test updating an opportunity."""
    opp_id = _create_dummy_opportunity(client)
    
    update_payload = {
        "name": "Updated Test Scholarship"
    }
    
    response = client.put(f"/api/v1/opportunities/{opp_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Scholarship"
    # Ensure other fields remain unchanged
    assert data["provider"] == "Test Trust"


def test_delete_opportunity(client):
    """Test deleting an opportunity."""
    opp_id = _create_dummy_opportunity(client)
    
    # Delete it
    response = client.delete(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get(f"/api/v1/opportunities/{opp_id}")
    assert response.status_code == 404
