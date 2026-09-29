"""
Search API Router
Handles semantic retrieval queries against ingested documents.
"""

from typing import Any, List, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.retrieval.search import SemanticSearcher

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
