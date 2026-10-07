import sys
import os
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings
from app.retrieval.search import SemanticSearcher
from app.retrieval.embedder import LocalEmbedder

def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def run_validation():
    # STEP 2: VERIFY POSTGRESQL / PGVECTOR
    print_header("STEP 2: DATABASE & PGVECTOR VERIFICATION")
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        # Check pgvector extension
        has_pgvector = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).fetchone()
        print(f"pgvector extension installed : {'YES' if has_pgvector else 'NO'}")
        
        # Check counts
        total = conn.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
        not_null = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")).scalar()
        nulls = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NULL")).scalar()
        
        # Check dimension
        dim = conn.execute(text("SELECT array_length(embedding::real[], 1) FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1")).scalar()
        
        print(f"Total chunks                 : {total}")
        print(f"Non-null embeddings          : {not_null}")
        print(f"Null embeddings              : {nulls}")
        print(f"Embedding dimension          : {dim}")

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    searcher = SemanticSearcher(db)
    
    # STEP 4: REALISTIC QUERIES
    print_header("STEP 4: REALISTIC QUERIES (Pure Semantic Search)")
    realistic_queries = [
        "What documents are required?",
        "What are the eligibility requirements?",
        "What are the academic requirements?",
        "What is the application process?",
        "What financial conditions are mentioned?",
        "What scholarship benefits are available?"
    ]
    
    for q in realistic_queries:
        print(f"\nQUERY: '{q}'")
        results = searcher.search(q, k=5)
        for i, res in enumerate(results):
            print(f"  Rank {i+1} | dist: {res['distance_score']:.4f} | chunk: {res['chunk_id'][:8]}... | {res['chunk_text'][:50].replace(chr(10), ' ')}...")
            
    # STEP 5: UNRELATED QUERIES
    print_header("STEP 5: UNRELATED QUERIES (Pure Semantic Search Top-K)")
    unrelated_queries = [
        "How do I repair a bicycle?",
        "Supercalifragilisticexpialidocious"
    ]
    
    for q in unrelated_queries:
        print(f"\nQUERY: '{q}'")
        results = searcher.search(q, k=5)
        for i, res in enumerate(results):
            print(f"  Rank {i+1} | dist: {res['distance_score']:.4f} | chunk: {res['chunk_id'][:8]}... | {res['chunk_text'][:50].replace(chr(10), ' ')}...")
            
    # STEP 8: TOP-K BEHAVIOR
    print_header("STEP 8: TOP-K BEHAVIOR VERIFICATION")
    q_topk = "eligibility requirements"
    print(f"Query: '{q_topk}'")
    for k_val in [1, 3, 5]:
        results = searcher.search(q_topk, k=k_val)
        print(f"  Requested k={k_val}, Returned count={len(results)}")
        
    # STEP 9: DETERMINISM
    print_header("STEP 9: DETERMINISM VERIFICATION")
    q_det = "application process"
    results1 = searcher.search(q_det, k=3)
    results2 = searcher.search(q_det, k=3)
    
    ids_1 = [r['chunk_id'] for r in results1]
    ids_2 = [r['chunk_id'] for r in results2]
    
    if ids_1 == ids_2:
        print(f"  Determinism OK: Multiple runs yielded identical chunk order.")
    else:
        print(f"  Determinism FAILED: {ids_1} vs {ids_2}")
        
    db.close()
    
    # STEP 7: TEST EXISTING API (Mocking via TestClient to avoid needing server running)
    print_header("STEP 7: API VALIDATION (/api/v1/search/semantic)")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/search/semantic", params={"query": "scholarship benefits", "k": 2})
        print(f"  HTTP Status : {response.status_code}")
        if response.status_code == 200:
            api_res = response.json()
            print(f"  Results     : {len(api_res)}")
            if len(api_res) > 0:
                print(f"  Top Match   : {api_res[0].get('chunk_text', '')[:50].replace(chr(10), ' ')}...")
                print(f"  Score       : {api_res[0].get('distance_score', 'N/A')}")
        else:
            print(f"  API Error   : {response.text}")
    except Exception as e:
        print(f"  Could not run TestClient API validation: {e}")

if __name__ == "__main__":
    run_validation()
