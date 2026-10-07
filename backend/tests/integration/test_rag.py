"""
Integration Tests for RAG Engine
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.models.document import SourceDocument, DocumentChunk
from app.models.opportunity import Opportunity
from pgvector.sqlalchemy import Vector

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
def client(override_db, monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "mock")
    return TestClient(app)

@pytest.fixture
def seed_rag_data(db_session, monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "mock")
    """Seed db with controlled test documents and chunks for RAG."""
    doc_a = SourceDocument(
        id=uuid.uuid4(), title="Doc A", source_url="doc_a.pdf",
        document_type="Guideline", file_path="/fake/a.pdf",
        ingestion_status="Processed"
    )
    
    doc_b = SourceDocument(
        id=uuid.uuid4(), title="Doc B", source_url="doc_b.pdf",
        document_type="Guideline", file_path="/fake/b.pdf",
        ingestion_status="Processed"
    )
    
    opp_a = Opportunity(
        id=uuid.uuid4(), name="Opportunity A", opportunity_type="Scholarship",
        provider="Test Provider", description="A", education_level=["UG"], status="Active",
        source_document_id=doc_a.id
    )
    opp_b = Opportunity(
        id=uuid.uuid4(), name="Opportunity B", opportunity_type="Scholarship",
        provider="Test Provider", description="B", education_level=["UG"], status="Active",
        source_document_id=doc_b.id
    )
    
    from app.retrieval.embedder import LocalEmbedder
    embedder = LocalEmbedder()
    
    content_a = "Documents required for Opportunity A include Aadhar card and Income certificate."
    content_b = "Documents required for Opportunity B include PAN card and 10th marksheet."
    
    emb_a = embedder.embed_query(content_a)
    emb_b = embedder.embed_query(content_b)
    
    chunk_a = DocumentChunk(
        id=uuid.uuid4(), source_document_id=doc_a.id, content=content_a,
        chunk_index=0, page_number=1, embedding=emb_a
    )
    
    chunk_b = DocumentChunk(
        id=uuid.uuid4(), source_document_id=doc_b.id, content=content_b,
        chunk_index=0, page_number=1, embedding=emb_b
    )
    
    db_session.add_all([opp_a, opp_b, doc_a, doc_b, chunk_a, chunk_b])
    db_session.commit()
    
    # Refresh BM25 index
    from app.retrieval.keyword_search import KeywordSearcher
    KeywordSearcher().refresh(db_session)
    
    return {"opp_a": opp_a, "opp_b": opp_b, "doc_a": doc_a, "doc_b": doc_b, "chunk_a": chunk_a, "chunk_b": chunk_b}

def test_rag_context_retrieval(client: TestClient, db_session, seed_rag_data):
    """Test 1 - Context Retrieval: Send a query and verify sources and answer are returned."""
    payload = {"query": "What documents are required for Opportunity A?"}
    
    response = client.post("/api/v1/rag/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "sources" in data
    
    # FakeListChatModel returns "I don't know based on the provided documents."
    assert data["answer"] == "I don't know based on the provided documents."
    
    sources = data["sources"]
    assert len(sources) > 0
    
    # Ensure source chunks are properly populated
    source = sources[0]
    assert "chunk_id" in source
    assert "document_id" in source
    assert "opportunity_id" in source

def test_rag_opportunity_filtering(client: TestClient, db_session, seed_rag_data):
    """Test 2 - Opportunity Filtering: Verify passing an opportunity_id scopes the retrieval."""
    opp_a_id = str(seed_rag_data["opp_a"].id)
    opp_b_id = str(seed_rag_data["opp_b"].id)
    
    # Query for "documents required", but filter to Opportunity A
    payload = {"query": "documents required", "opportunity_id": opp_a_id}
    
    response = client.post("/api/v1/rag/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    sources = data["sources"]
    assert len(sources) > 0
    
    # Verify all returned sources belong to Opportunity A
    for src in sources:
        assert src["opportunity_id"] == opp_a_id
        assert src["opportunity_id"] != opp_b_id

def test_rag_no_context(client: TestClient, db_session):
    """Test 4 - No Context: Test a query for which no relevant document context exists."""
    # A completely random query that won't match anything
    payload = {"query": "Supercalifragilisticexpialidocious"}
    
    response = client.post("/api/v1/rag/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should safely return no sources and a grounded "I don't know" answer
    assert data["answer"] == "I don't know based on the provided documents."
    assert len(data["sources"]) == 0

def test_rag_top_k(client: TestClient, db_session, seed_rag_data):
    """Test 5 - top_k: Verify top_k bounds the source context chunks."""
    payload = {"query": "documents", "top_k": 1}
    
    response = client.post("/api/v1/rag/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    sources = data["sources"]
    assert len(sources) <= 1
