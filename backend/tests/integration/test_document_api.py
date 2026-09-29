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


def test_upload_document(dummy_pdf):
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
    return result["id"]


def test_get_documents(dummy_pdf):
    """Test retrieving list of documents."""
    test_upload_document(dummy_pdf)
    
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test Scholarship Guidelines"


def test_get_document_by_id(dummy_pdf):
    """Test retrieving a specific document."""
    doc_id = test_upload_document(dummy_pdf)
    
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
