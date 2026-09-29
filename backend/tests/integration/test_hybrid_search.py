"""
Integration Tests for Keyword and Hybrid Search API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.document import DocumentChunk, SourceDocument
from app.api.deps import get_db
from app.core.config import settings
from app.retrieval.embedder import LocalEmbedder
from app.retrieval.keyword_search import KeywordSearcher

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

def test_keyword_search_api(client, db_session):
    """Test the /api/v1/search/keyword endpoint."""
    doc = SourceDocument(title="Test Keyword Doc", ingestion_status="Processed")
    db_session.add(doc)
    db_session.commit()
    
    # We don't necessarily need embeddings for pure keyword search, but the column might not be nullable
    # Let's provide dummy embeddings
    dummy_emb = [0.0] * 384
    
    chunk_1 = DocumentChunk(
        source_document_id=doc.id, content="This is about machine learning and artificial intelligence.", 
        chunk_index=0, embedding=dummy_emb
    )
    chunk_2 = DocumentChunk(
        source_document_id=doc.id, content="This contains specific terminology like BM25 and TF-IDF.", 
        chunk_index=1, embedding=dummy_emb
    )
    
    db_session.add_all([chunk_1, chunk_2])
    db_session.commit()
    
    # Refresh keyword index inside test
    KeywordSearcher().refresh(db_session)
    
    response = client.get("/api/v1/search/keyword", params={"query": "bm25 terminology", "k": 1})
    assert response.status_code == 200
    
    results = response.json()
    assert len(results) == 1
    assert "BM25" in results[0]["chunk_text"]


def test_hybrid_search_api(client, db_session):
    """Test the /api/v1/search/hybrid endpoint."""
    embedder = LocalEmbedder()
    doc = SourceDocument(title="Test Hybrid Doc", ingestion_status="Processed")
    db_session.add(doc)
    db_session.commit()
    
    # Chunk 1 has exact keyword match but maybe slightly less semantic match conceptually
    text_1 = "The deadline for the exact scholarship 2025 is today."
    
    # Chunk 2 has high semantic match but no exact keyword
    text_2 = "Applications for the financial aid program close very soon."
    
    emb_1 = embedder.embed_query(text_1)
    emb_2 = embedder.embed_query(text_2)
    
    chunk_1 = DocumentChunk(source_document_id=doc.id, content=text_1, chunk_index=0, embedding=emb_1)
    chunk_2 = DocumentChunk(source_document_id=doc.id, content=text_2, chunk_index=1, embedding=emb_2)
    
    db_session.add_all([chunk_1, chunk_2])
    db_session.commit()
    
    # Refresh keyword index
    KeywordSearcher().refresh(db_session)
    
    response = client.get("/api/v1/search/hybrid", params={"query": "financial aid application", "k": 2})
    assert response.status_code == 200
    
    results = response.json()
    assert len(results) >= 1
    # Check that score exists (RRF score)
    assert "score" in results[0]
