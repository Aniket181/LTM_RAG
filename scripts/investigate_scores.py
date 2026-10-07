#!/usr/bin/env python
import sys
import os
import uuid

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.retrieval.hybrid_search import HybridSearcher
from app.models.document import DocumentChunk

# Connect
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

queries = [
    ("A. Legitimate query", "What documents are required for Opportunity A?"),
    ("B. No-context query", "Supercalifragilisticexpialidocious"),
    ("C. Opportunity filter query", "documents required")
]

db = SessionLocal()
try:
    searcher = HybridSearcher(db)
    
    for case_name, q in queries:
        print(f"\n{'='*60}\n{case_name}\nQUERY: '{q}'\n{'='*60}")
        
        # 1. Inspect raw semantic search scores
        print("\n--- Raw Semantic Search ---")
        semantic_results = searcher.semantic_searcher.search(q, k=5)
        for i, res in enumerate(semantic_results):
            print(f"  Rank {i+1} | chunk_id: {res['chunk_id'][:8]}... | dist: {res['distance_score']:.4f} | text: {res['chunk_text'][:30]}...")
            
        # 2. Inspect raw keyword search scores
        print("\n--- Raw Keyword Search ---")
        keyword_results = searcher.keyword_searcher.search(q, k=5, db=db)
        for i, res in enumerate(keyword_results):
            # KeywordSearcher maps score differently, let's just see it
            print(f"  Rank {i+1} | chunk_id: {res['chunk_id'][:8]}... | bm25 score: (hidden in chunk map usually) | text: {res['chunk_text'][:30]}...")

        # 3. Inspect hybrid search results
        print("\n--- Hybrid Search (Pre-filter) ---")
        hybrid_results = searcher.search(query=q, k=5)
        for i, res in enumerate(hybrid_results):
            dist = res.get('distance_score')
            dist_str = f"{dist:.4f}" if dist is not None else "None"
            print(f"  Rank {i+1} | chunk_id: {res['chunk_id'][:8]}... | dist: {dist_str} | RRF score: {res['score']:.5f}")
            
        # 4. RAGEngine filtering logic test
        print("\n--- RAGEngine Filter logic (dist > 0.8) ---")
        filtered = []
        for res in hybrid_results:
            dist = res.get("distance_score")
            if dist is not None and dist > 0.8:
                continue
            filtered.append(res)
            
        print(f"  Before: {len(hybrid_results)} -> After: {len(filtered)}")

finally:
    db.close()
