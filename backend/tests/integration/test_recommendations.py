"""
Integration Tests for Recommendation Engine
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.recommendations.engine import RecommendationEngine

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

def test_recommendation_filtering(client: TestClient, db_session):
    """Test that NOT_ELIGIBLE opportunities are filtered out."""
    student = Student(
        name="Test Student", education_level="UG", course="B.Tech",
        percentage=85.0, annual_family_income=200000.0,
        category="OBC", gender="Female", domicile="Maharashtra"
    )
    
    # Eligible opp
    opp1 = Opportunity(
        name="Eligible Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test scholarship",
        education_level=["UG"], maximum_income=300000.0, status="Active"
    )
    
    # Not Eligible opp (income too low max)
    opp2 = Opportunity(
        name="Not Eligible Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Test scholarship",
        education_level=["UG"], maximum_income=100000.0, status="Active"
    )
    
    db_session.add_all([student, opp1, opp2])
    db_session.commit()
    
    response = client.get(f"/api/v1/recommendations/{student.id}")
    assert response.status_code == 200
    data = response.json()
    
    names = [item["opportunity"]["name"] for item in data]
    assert "Eligible Scholarship" in names
    assert "Not Eligible Scholarship" not in names

def test_recommendation_deadline_urgency(client: TestClient, db_session):
    """Test that nearer deadlines rank higher."""
    student = Student(
        name="Urgency Student", education_level="UG", course="B.Tech"
    )
    
    # Tomorrow
    opp_urgent = Opportunity(
        name="Urgent Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Urgent",
        education_level=["UG"], status="Active",
        closing_date=date.today() + timedelta(days=1)
    )
    
    # In 6 months
    opp_later = Opportunity(
        name="Later Scholarship", opportunity_type="Scholarship",
        provider="Test Provider", description="Later",
        education_level=["UG"], status="Active",
        closing_date=date.today() + timedelta(days=180)
    )
    
    db_session.add_all([student, opp_urgent, opp_later])
    db_session.commit()
    
    response = client.get(f"/api/v1/recommendations/{student.id}")
    assert response.status_code == 200
    data = response.json()
    
    urgent_item = next(item for item in data if item["opportunity"]["name"] == "Urgent Scholarship")
    later_item = next(item for item in data if item["opportunity"]["name"] == "Later Scholarship")
    
    # Check that rank for urgent is better (lower rank number)
    assert urgent_item["rank"] < later_item["rank"]
    
    # Check that score for urgent is higher
    urgent_score = urgent_item["score"]["deadline_score"]
    later_score = later_item["score"]["deadline_score"]
    assert urgent_score > later_score
    
def test_recommendation_api_output_and_transparency(client: TestClient, db_session):
    """Test API output structure and score calculation transparency."""
    student = Student(
        name="Test Student Output", education_level="UG", course="B.Tech"
    )
    opp = Opportunity(
        name="Test Scholarship Output", opportunity_type="Scholarship",
        provider="Test Provider", description="Output test",
        education_level=["UG"], status="Active"
    )
    db_session.add_all([student, opp])
    db_session.commit()
    
    response = client.get(f"/api/v1/recommendations/{student.id}")
    assert response.status_code == 200
    data = response.json()
    
    item = next(item for item in data if item["opportunity"]["name"] == "Test Scholarship Output")
    
    assert "rank" in item
    assert "opportunity" in item
    assert "eligibility" in item
    assert "score" in item
    
    score = item["score"]
    assert "deadline_score" in score
    assert "financial_need_score" in score
    assert "academic_merit_score" in score
    assert "demographic_match_score" in score
    assert "total_score" in score
    assert "reasons" in score
    
    # Verify sum
    assert score["total_score"] == (
        score["deadline_score"] +
        score["financial_need_score"] +
        score["academic_merit_score"] +
        score["demographic_match_score"]
    )
    
def test_recommendation_top_k(client: TestClient, db_session):
    """Test top_k filtering."""
    student = Student(name="Top K Student", education_level="UG", course="B.Tech")
    
    opps = [
        Opportunity(
            name=f"Scholarship {i}", opportunity_type="Scholarship",
            provider="Provider", description="Desc",
            education_level=["UG"], status="Active"
        )
        for i in range(5)
    ]
    
    db_session.add(student)
    db_session.add_all(opps)
    db_session.commit()
    
    response = client.get(f"/api/v1/recommendations/{student.id}?top_k=2")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
