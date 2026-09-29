"""
Integration Tests for Eligibility Engine
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.eligibility_check_log import EligibilityCheckLog

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

def test_eligibility_strict_pass(client: TestClient, db_session):
    """Test when a student perfectly matches all criteria."""
    student = Student(
        name="Test Student", education_level="UG", course="B.Tech",
        percentage=85.0, annual_family_income=200000.0,
        category="OBC", gender="Female", domicile="Maharashtra"
    )
    opp = Opportunity(
        name="Test Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test scholarship for academic, financial, and demographic eligibility testing",
        education_level=["UG"], course=["B.Tech"], minimum_percentage=80.0,
        maximum_income=250000.0, category=["OBC", "SC"], gender="Female",
        state="Maharashtra", status="Active"
    )
    db_session.add_all([student, opp])
    db_session.commit()
    
    payload = {"student_id": str(student.id), "opportunity_ids": [str(opp.id)]}
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    evaluations = data["evaluations"]
    assert len(evaluations) == 1
    assert evaluations[0]["overall_status"] == "ELIGIBLE"
    
    # Verify DB log
    log = db_session.query(EligibilityCheckLog).filter_by(student_id=student.id).first()
    assert log is not None
    assert log.overall_status == "ELIGIBLE"


def test_eligibility_strict_fail_financial(client: TestClient, db_session):
    """Test failure due to exceeding income."""
    student = Student(
        name="Rich Student", education_level="UG", course="B.Tech",
        percentage=90.0, annual_family_income=500000.0, category="General"
    )
    opp = Opportunity(
        name="Poor Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test scholarship with a maximum family income requirement",
        education_level=["UG"], maximum_income=250000.0, status="Active"
    )
    db_session.add_all([student, opp])
    db_session.commit()
    
    payload = {"student_id": str(student.id), "opportunity_ids": [str(opp.id)]}
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    
    data = response.json()
    assert data["evaluations"][0]["overall_status"] == "NOT_ELIGIBLE"
    
    # FinancialRule should have failed
    rules = data["evaluations"][0]["rule_results"]
    fin_rule = next(r for r in rules if r["rule_name"] == "FinancialRule")
    assert fin_rule["result"] == "FAIL"


def test_eligibility_strict_fail_academic(client: TestClient, db_session):
    """Test failure due to low marks."""
    student = Student(
        name="Low Marks Student", education_level="UG", course="B.Tech",
        percentage=60.0, annual_family_income=100000.0, category="General"
    )
    opp = Opportunity(
        name="Merit Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test merit scholarship with a minimum academic percentage requirement",
        education_level=["UG"], course=["B.Tech"], minimum_percentage=80.0, status="Active"
    )
    db_session.add_all([student, opp])
    db_session.commit()
    
    payload = {"student_id": str(student.id), "opportunity_ids": [str(opp.id)]}
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    
    data = response.json()
    assert data["evaluations"][0]["overall_status"] == "NOT_ELIGIBLE"


def test_eligibility_unknown_missing_data(client: TestClient, db_session):
    """Test unknown status due to missing student data."""
    student = Student(
        name="Missing Data Student", education_level="UG", course="B.Tech",
        category="General"
        # annual_family_income is missing
    )
    opp = Opportunity(
        name="Income Based Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test income-based scholarship used to verify missing income handling",
        education_level=["UG"], maximum_income=250000.0, status="Active"
    )
    db_session.add_all([student, opp])
    db_session.commit()
    
    payload = {"student_id": str(student.id), "opportunity_ids": [str(opp.id)]}
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    
    data = response.json()
    assert data["evaluations"][0]["overall_status"] == "INSUFFICIENT_INFORMATION"
