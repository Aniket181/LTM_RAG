"""
Unit Tests for Database Models and Schemas
Tests table mapping, relations, serialization, and Pydantic schema validation using an in-memory SQLite database.
"""

from datetime import date
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.document import DocumentChunk, SourceDocument
from app.models.eligibility_check_log import EligibilityCheckLog
from app.models.opportunity import Opportunity
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.opportunity import OpportunityCreate, OpportunityResponse


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_student_model_creation_and_to_dict(db_session):
    """Verify Student model persistence and serialization."""
    student = Student(
        name="Aarav Sharma",
        education_level="UG",
        course="B.Tech",
        branch="Computer Science",
        year_of_study=3,
        semester=5,
        cgpa=8.85,
        percentage=85.5,
        annual_family_income=250000.0,
        state="Maharashtra",
        domicile="Maharashtra",
        category="OBC",
        gender="Male",
        institution_type="Government",
        age=20,
        academic_interests=["AI", "Distributed Systems"],
        career_interests=["Software Engineering", "Research"],
        nationality="Indian",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    assert student.id is not None
    assert isinstance(student.id, uuid.UUID)
    assert student.name == "Aarav Sharma"
    assert student.created_at is not None
    assert student.updated_at is not None

    # Test dictionary conversion
    d = student.to_dict()
    assert d["name"] == "Aarav Sharma"
    assert d["cgpa"] == 8.85
    assert d["category"] == "OBC"
    assert "AI" in d["academic_interests"]

    # Test Pydantic validation from attribute
    schema_obj = StudentResponse.model_validate(student)
    assert schema_obj.course == "B.Tech"
    assert schema_obj.cgpa == 8.85


def test_source_document_and_chunks_relationship(db_session):
    """Verify SourceDocument and cascading DocumentChunks relationship."""
    doc = SourceDocument(
        title="AICTE Pragati Scholarship Scheme Guidelines",
        source_url="https://www.aicte-india.org/schemes/students-development-schemes/Pragati",
        document_type="Official Guidelines",
        academic_year="2025-2026",
        last_verified_date=date(2026, 1, 15),
        ingestion_status="ingested",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    chunk1 = DocumentChunk(
        source_document_id=doc.id,
        content="Eligibility: Scheme open for girl students admitted to first year of Degree programme.",
        chunk_index=0,
        section_title="Eligibility Criteria",
        page_number=1,
        chunk_metadata={"section": "eligibility", "scheme": "Pragati"},
        embedding_id="emb_001",
    )
    chunk2 = DocumentChunk(
        source_document_id=doc.id,
        content="Amount: Scholarship of Rs. 50,000 per annum for every year of study.",
        chunk_index=1,
        section_title="Financial Assistance",
        page_number=2,
        chunk_metadata={"section": "benefits", "scheme": "Pragati"},
        embedding_id="emb_002",
    )
    db_session.add_all([chunk1, chunk2])
    db_session.commit()

    db_session.refresh(doc)
    assert len(doc.chunks) == 2
    assert doc.chunks[0].chunk_index == 0
    assert doc.chunks[1].chunk_index == 1

    # Test cascade delete
    db_session.delete(doc)
    db_session.commit()

    remaining_chunks = db_session.query(DocumentChunk).all()
    assert len(remaining_chunks) == 0


def test_opportunity_model_and_validation(db_session):
    """Verify Opportunity creation, relations, and Pydantic validation."""
    opp = Opportunity(
        name="Central Sector Scheme of Scholarship (CSSS)",
        provider="Ministry of Education, Government of India",
        description="Merit-cum-means scholarship for university and college students.",
        opportunity_type="Scholarship",
        education_level=["UG", "PG"],
        course=["B.Tech", "B.Sc", "B.Com", "BA"],
        minimum_percentage=80.0,
        maximum_income=450000.0,
        category=["General", "OBC", "SC", "ST", "EWS"],
        gender="Any",
        amount=20000.0,
        duration="Annual",
        status="Active",
    )
    db_session.add(opp)
    db_session.commit()
    db_session.refresh(opp)

    assert opp.id is not None
    assert opp.name.startswith("Central Sector")
    assert opp.maximum_income == 450000.0
    assert "UG" in opp.education_level

    # Validate with Pydantic
    resp = OpportunityResponse.model_validate(opp)
    assert resp.opportunity_type == "Scholarship"
    assert resp.provider == "Ministry of Education, Government of India"


def test_eligibility_check_log(db_session):
    """Verify logging of eligibility checks."""
    student = Student(
        name="Riya Patel",
        education_level="UG",
        course="B.Tech",
        category="General",
    )
    opp = Opportunity(
        name="Test Scholarship",
        provider="Trust",
        description="Demo test",
        opportunity_type="Scholarship",
        education_level=["UG"],
        status="Active",
    )
    db_session.add_all([student, opp])
    db_session.commit()

    log = EligibilityCheckLog(
        student_id=student.id,
        opportunity_id=opp.id,
        overall_status="ELIGIBLE",
        rule_results=[
            {
                "rule_name": "AcademicRule",
                "condition": "education_level == UG",
                "student_value": "UG",
                "required_value": "UG",
                "result": "PASS",
                "detail": "Education level matches",
            }
        ],
        summary="Student meets all basic criteria.",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    assert log.id is not None
    assert log.overall_status == "ELIGIBLE"
    assert len(log.rule_results) == 1
    assert log.student.name == "Riya Patel"
    assert log.opportunity.name == "Test Scholarship"
