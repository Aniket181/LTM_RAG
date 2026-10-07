import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.retrieval.keyword_search import KeywordSearcher
from app.retrieval.search import SemanticSearcher
from app.models.document import DocumentChunk

def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def run_validation():
    # Setup
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    keyword_searcher = KeywordSearcher()
    # Explicitly refresh cache
    keyword_searcher.refresh(db)

    # STEP 2: VERIFY CORPUS
    print_header("STEP 2: VERIFY CORPUS")
    total = db.query(DocumentChunk).count()
    print(f"Total document chunks in DB: {total}")
    print(f"BM25 Indexed chunks        : {len(keyword_searcher._chunks) if keyword_searcher._chunks else 0}")
    
    # STEP 3 & 4: TEST EXACT KEYWORD QUERIES
    print_header("STEP 3 & 4: EXACT KEYWORD QUERIES")
    exact_queries = [
        "UGC",
        "scholarship",
        "eligibility",
        "renewal",
        "documents",
        "institutions"
    ]
    
    for q in exact_queries:
        print(f"\nQUERY: '{q}'")
        res = keyword_searcher.search(q, k=3, db=db)
        if not res:
            print("  No matches found.")
        for i, r in enumerate(res):
            print(f"  Rank {i+1} | BM25 Score: {r['score']:.4f} | Chunk ID: {r['chunk_id'][:8]}...")
            print(f"    Preview: {r['chunk_text'][:80].replace(chr(10), ' ')}...")
            
    # STEP 5: NO-MATCH QUERY
    print_header("STEP 5: NO-MATCH QUERY")
    q_none = "xyzabc123nonexistent"
    print(f"QUERY: '{q_none}'")
    res_none = keyword_searcher.search(q_none, k=5, db=db)
    print(f"  Returned count: {len(res_none)}")

    # STEP 6: TOP-K BEHAVIOR
    print_header("STEP 6: TOP-K BEHAVIOR")
    q_topk = "eligibility"
    print(f"QUERY: '{q_topk}'")
    for k_val in [1, 3, 5]:
        res_topk = keyword_searcher.search(q_topk, k=k_val, db=db)
        print(f"  Requested k={k_val}, Returned count={len(res_topk)}")

    # STEP 9: COMPARE WITH SEMANTIC SEARCH
    print_header("STEP 9: COMPARE WITH SEMANTIC SEARCH")
    semantic_searcher = SemanticSearcher(db)
    compare_queries = ["eligibility", "documents required"]
    
    for q in compare_queries:
        print(f"\nQUERY: '{q}'")
        print("  -- Keyword (BM25) --")
        k_res = keyword_searcher.search(q, k=3, db=db)
        for i, r in enumerate(k_res):
            print(f"    Rank {i+1} | Score: {r['score']:.4f} | Text: {r['chunk_text'][:50].replace(chr(10), ' ')}...")
            
        print("  -- Semantic (pgvector) --")
        s_res = semantic_searcher.search(q, k=3)
        for i, r in enumerate(s_res):
            print(f"    Rank {i+1} | Dist: {r['distance_score']:.4f} | Text: {r['chunk_text'][:50].replace(chr(10), ' ')}...")

    db.close()
    
    # STEP 7: BM25 API
    print_header("STEP 7: BM25 API VALIDATION")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/search/keyword", params={"query": "eligibility", "k": 2})
        print(f"  HTTP Status : {response.status_code}")
        if response.status_code == 200:
            api_res = response.json()
            print(f"  Results     : {len(api_res)}")
            if len(api_res) > 0:
                print(f"  Top Match   : {api_res[0].get('chunk_text', '')[:50].replace(chr(10), ' ')}...")
                print(f"  Score       : {api_res[0].get('score', 'N/A')}")
    except Exception as e:
        print(f"  Could not run TestClient API validation: {e}")

if __name__ == "__main__":
    run_validation()
