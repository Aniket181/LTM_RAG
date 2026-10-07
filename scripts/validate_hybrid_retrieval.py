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
from app.retrieval.hybrid_search import HybridSearcher
from app.models.document import DocumentChunk

def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def run_validation():
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    hybrid_searcher = HybridSearcher(db)
    # Refresh keyword search index explicitly just in case
    hybrid_searcher.keyword_searcher.refresh(db)

    # STEP 3: VERIFY CORPUS
    print_header("STEP 3: VERIFY CORPUS")
    total = db.query(DocumentChunk).count()
    not_null = db.query(DocumentChunk).filter(DocumentChunk.embedding.is_not(None)).count()
    bm25_count = len(hybrid_searcher.keyword_searcher._chunks) if hybrid_searcher.keyword_searcher._chunks else 0
    print(f"Total document chunks: {total}")
    print(f"Chunks with embeddings: {not_null}")
    print(f"BM25 indexed chunks: {bm25_count}")

    # STEP 4: HYBRID TEST QUERIES
    print_header("STEP 4: HYBRID TEST QUERIES")
    hybrid_queries = [
        "eligibility",
        "documents required",
        "scholarship benefits",
        "application process",
        "financial conditions"
    ]
    
    for q in hybrid_queries:
        print(f"\nQUERY: '{q}'")
        results = hybrid_searcher.search(q, k=3)
        for i, res in enumerate(results):
            print(f"  Rank {i+1} | Chunk: {res['chunk_id'][:8]}... | RRF Score: {res['score']:.5f} | Preview: {res['chunk_text'][:50].replace(chr(10), ' ')}...")

    # STEP 5 & 6: COMPARE THREE RETRIEVERS & RRF VALIDATION
    print_header("STEP 5 & 6: COMPARE THREE RETRIEVERS & RRF VALIDATION")
    compare_queries = ["eligibility", "documents required"]
    
    for q in compare_queries:
        print(f"\n{'*'*40}\nQUERY: '{q}'\n{'*'*40}")
        pool_size = max(5 * 2, 20)
        sem_res = hybrid_searcher.semantic_searcher.search(q, k=pool_size)
        key_res = hybrid_searcher.keyword_searcher.search(q, k=pool_size, db=db)
        hyb_res = hybrid_searcher.search(q, k=5)
        
        print("\n--- A. Semantic Ranking (Top 3) ---")
        sem_map = {}
        for i, r in enumerate(sem_res[:3]):
            print(f"  {i+1}. Chunk: {r['chunk_id'][:8]}... | Dist: {r['distance_score']:.4f}")
        for i, r in enumerate(sem_res):
            sem_map[r['chunk_id']] = i
            
        print("\n--- B. Keyword Ranking (Top 3) ---")
        key_map = {}
        for i, r in enumerate(key_res[:3]):
            print(f"  {i+1}. Chunk: {r['chunk_id'][:8]}... | BM25: {r['score']:.4f}")
        for i, r in enumerate(key_res):
            key_map[r['chunk_id']] = i
            
        print("\n--- C. Hybrid RRF Ranking (Top 3) ---")
        for i, r in enumerate(hyb_res[:3]):
            c_id = r['chunk_id']
            s_rank = sem_map.get(c_id, -1)
            k_rank = key_map.get(c_id, -1)
            
            # Reconstruct RRF score calculation (k=60)
            rrf_k = 60
            s_score = 1.0 / (rrf_k + s_rank + 1) if s_rank >= 0 else 0.0
            k_score = 1.0 / (rrf_k + k_rank + 1) if k_rank >= 0 else 0.0
            computed = s_score + k_score
            
            print(f"  {i+1}. Chunk: {c_id[:8]}... | RRF Score: {r['score']:.5f}")
            print(f"     -> Semantic Rank: {s_rank if s_rank>=0 else 'N/A'} (Contribution: {s_score:.5f})")
            print(f"     -> Keyword Rank : {k_rank if k_rank>=0 else 'N/A'} (Contribution: {k_score:.5f})")
            print(f"     -> Verified Math: {computed:.5f} == {r['score']:.5f}")

    # STEP 7: TOP-K BEHAVIOR
    print_header("STEP 7: TOP-K BEHAVIOR")
    q_topk = "eligibility"
    print(f"Query: '{q_topk}'")
    for k_val in [1, 3, 5]:
        results = hybrid_searcher.search(q_topk, k=k_val)
        c_ids = [r['chunk_id'] for r in results]
        is_unique = len(set(c_ids)) == len(c_ids)
        print(f"  Requested k={k_val} -> Returned count={len(results)} | Unique IDs: {is_unique}")

    # STEP 8: NO-MATCH / IRRELEVANT QUERY
    print_header("STEP 8: NO-MATCH / IRRELEVANT QUERY")
    irr_queries = ["xyzabc123nonexistent", "How do I repair a bicycle?"]
    for q in irr_queries:
        print(f"\nQUERY: '{q}'")
        res = hybrid_searcher.search(q, k=5)
        print(f"  Returned {len(res)} chunks from HybridSearcher.")
        for i, r in enumerate(res[:2]):
            dist = r.get('distance_score')
            dist_str = f"{dist:.4f}" if dist is not None else "N/A"
            print(f"  Rank {i+1} | RRF Score: {r['score']:.5f} | Dist: {dist_str} | Chunk: {r['chunk_id'][:8]}...")
        # Check against RAGEngine relevance threshold
        passed = sum(1 for r in res if r.get('distance_score') is None or r.get('distance_score') <= 0.40)
        print(f"  Chunks passing RAG relevance threshold (dist <= 0.40): {passed}")

    # STEP 10: DETERMINISM
    print_header("STEP 10: DETERMINISM")
    q_det = "eligibility"
    r1 = [r['chunk_id'] for r in hybrid_searcher.search(q_det, k=5)]
    r2 = [r['chunk_id'] for r in hybrid_searcher.search(q_det, k=5)]
    if r1 == r2:
        print("  Determinism OK: Both runs yielded exact same chunk ordering.")
    else:
        print(f"  Determinism FAILED:\nRun 1: {r1}\nRun 2: {r2}")

    db.close()
    
    # STEP 9: API VALIDATION
    print_header("STEP 9: API VALIDATION (/api/v1/search/hybrid)")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/api/v1/search/hybrid", params={"query": "financial conditions", "k": 3})
        print(f"  HTTP Status : {response.status_code}")
        if response.status_code == 200:
            api_res = response.json()
            print(f"  Results     : {len(api_res)}")
            if len(api_res) > 0:
                print(f"  Top Match   : {api_res[0].get('chunk_text', '')[:50].replace(chr(10), ' ')}...")
                print(f"  RRF Score   : {api_res[0].get('score', 'N/A'):.5f}")
    except Exception as e:
        print(f"  Could not run TestClient API validation: {e}")

if __name__ == "__main__":
    run_validation()
