"""
Integration Tests for Semantic Search API & pgvector functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.models.document import DocumentChunk, SourceDocument
from app.api.deps import get_db
from app.core.config import settings
from app.retrieval.embedder import LocalEmbedder

# Connect to the real PostgreSQL database for pgvector support
# We will use nested transactions to roll back any changes made during tests
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def real_db_engine():
    """Ensure the schema exists."""
    # We assume Alembic has been run. create_all is safe if tables exist.
    # Base.metadata.create_all(bind=engine) 
    yield engine


@pytest.fixture
def db_session(real_db_engine):
    """
    Creates a new database session for a test with a SAVEPOINT.
    Rolls back the transaction after the test to keep the DB clean.
    """
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


def test_embedder_initialization():
    """Test that the local BGE model loads and generates 384D embeddings."""
    embedder = LocalEmbedder()
    assert embedder._model is not None
    
    # Safe diagnostic print
    model_name = getattr(settings, "embedding_model", "")
    import os
    if os.path.isdir(model_name):
        print(f"\n[DIAGNOSTIC] Using Local Filesystem Path: {model_name}")
        assert embedder._model.model_kwargs.get('local_files_only') is True
        assert embedder._model.model_kwargs.get('trust_remote_code') is False
    else:
        print(f"\n[DIAGNOSTIC] Using Hugging Face Model ID: {model_name}")
    
    # Test batch embedding
    vectors = embedder.embed_documents(["This is a test chunk."])
    assert len(vectors) == 1
    assert len(vectors[0]) == 384
    
    # Test query embedding
    q_vec = embedder.embed_query("test query")
    assert len(q_vec) == 384


def test_pgvector_storage_and_retrieval(db_session):
    """Test storing and retrieving a DocumentChunk with pgvector."""
    # 1. Create a parent SourceDocument
    doc = SourceDocument(title="Vector Test Doc", ingestion_status="Processed")
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    
    # 2. Create embedding
    embedder = LocalEmbedder()
    test_text = "Vector storage is working properly in PostgreSQL."
    embedding = embedder.embed_query(test_text)
    
    # 3. Create chunk
    chunk = DocumentChunk(
        source_document_id=doc.id,
        content=test_text,
        chunk_index=0,
        embedding=embedding
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)
    
    # 4. Retrieve and verify
    retrieved = db_session.query(DocumentChunk).filter_by(id=chunk.id).first()
    assert retrieved is not None
    assert retrieved.embedding is not None
    assert len(retrieved.embedding) == 384
    

def test_semantic_search_api(client, db_session):
    """Test the /api/v1/search/semantic endpoint."""
    # Setup test data
    embedder = LocalEmbedder()
    
    doc = SourceDocument(title="Scholarship API Doc", ingestion_status="Processed")
    db_session.add(doc)
    db_session.commit()
    
    # Create one relevant chunk and one irrelevant chunk
    relevant_text = "This scholarship is for women in STEM engineering."
    irrelevant_text = "The quick brown fox jumps over the lazy dog."
    
    emb_rel = embedder.embed_query(relevant_text)
    emb_irr = embedder.embed_query(irrelevant_text)
    
    chunk_rel = DocumentChunk(
        source_document_id=doc.id, content=relevant_text, chunk_index=0, embedding=emb_rel
    )
    chunk_irr = DocumentChunk(
        source_document_id=doc.id, content=irrelevant_text, chunk_index=1, embedding=emb_irr
    )
    
    db_session.add_all([chunk_rel, chunk_irr])
    db_session.commit()
    
    # Execute search
    response = client.get("/api/v1/search/semantic", params={"query": "engineering female students", "k": 2})
    assert response.status_code == 200
    
    results = response.json()
    assert len(results) == 2
    
    # The relevant chunk should be first (lower distance score)
    assert results[0]["chunk_text"] == relevant_text
    assert "distance_score" in results[0]
    assert results[0]["distance_score"] < results[1]["distance_score"]
    assert results[0]["document_title"] == "Scholarship API Doc"
