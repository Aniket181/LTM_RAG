"""
Integration Tests for Documents API
Tests file upload and metadata retrieval at /api/v1/documents
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from io import BytesIO

from app.main import app
from app.models import Base
from app.api.deps import get_db
from reportlab.pdfgen import canvas

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


@pytest.fixture
def dummy_pdf():
    """Creates a dummy PDF file in memory for testing uploads."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "This is a test document for scholarship guidelines.")
    c.drawString(100, 730, "Eligibility: Must have 80% marks.")
    c.save()
    buffer.seek(0)
    return buffer


def _upload_dummy_document(dummy_pdf, client):
    """Helper to upload a document and return its ID."""
    files = {
        "file": ("test_scholarship.pdf", dummy_pdf, "application/pdf")
    }
    data = {
        "title": "Test Scholarship Guidelines",
        "document_type": "Scholarship Guideline"
    }
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 201
    return response.json()["id"]


def test_upload_document(dummy_pdf, client):
    """Test uploading a new PDF document."""
    files = {
        "file": ("test_scholarship.pdf", dummy_pdf, "application/pdf")
    }
    data = {
        "title": "Test Scholarship Guidelines",
        "document_type": "Scholarship Guideline"
    }
    
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 201
    result = response.json()
    assert result["title"] == "Test Scholarship Guidelines"
    assert result["ingestion_status"] == "Pending"
    assert "id" in result


def test_get_documents(dummy_pdf, client):
    """Test retrieving list of documents."""
    doc_id = _upload_dummy_document(dummy_pdf, client)
    
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    # Find the document we just uploaded by its ID
    matching_docs = [doc for doc in data if doc["id"] == doc_id]
    assert len(matching_docs) == 1
    assert matching_docs[0]["title"] == "Test Scholarship Guidelines"


def test_get_document_by_id(dummy_pdf, client):
    """Test retrieving a specific document."""
    doc_id = _upload_dummy_document(dummy_pdf, client)
    
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
