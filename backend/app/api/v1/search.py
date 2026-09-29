"""
Search API Router
Handles semantic retrieval queries against ingested documents.
"""

from typing import Any, List, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.retrieval.search import SemanticSearcher
from app.retrieval.keyword_search import KeywordSearcher
from app.retrieval.hybrid_search import HybridSearcher

router = APIRouter()


@router.get("/semantic")
def search_semantic(
    query: str = Query(..., description="The search query"),
    k: int = Query(5, ge=1, le=20, description="Number of top results to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform a semantic similarity search using pgvector cosine distance.
    Returns the top K most relevant document chunks along with their provenance data.
    """
    searcher = SemanticSearcher(db)
    results = searcher.search(query=query, k=k)
    return results


@router.get("/keyword")
def search_keyword(
    query: str = Query(..., description="The search query"),
    k: int = Query(5, ge=1, le=20, description="Number of top results to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform a keyword search using BM25.
    Returns the top K most relevant document chunks based on vocabulary match.
    """
    searcher = KeywordSearcher()
    results = searcher.search(query=query, k=k, db=db)
    return results


@router.get("/hybrid")
def search_hybrid(
    query: str = Query(..., description="The search query"),
    k: int = Query(5, ge=1, le=20, description="Number of top results to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Perform a hybrid search combining semantic (pgvector) and keyword (BM25) matching.
    Uses Reciprocal Rank Fusion (RRF) for scoring.
    """
    searcher = HybridSearcher(db)
    results = searcher.search(query=query, k=k)
    return results
