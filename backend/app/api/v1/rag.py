"""
RAG API Router
Exposes the RAG endpoints for Q&A.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.rag import AskRequest, AnswerResponse
from app.rag.engine import RAGEngine

router = APIRouter()

@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question and receive a grounded answer with source attribution.
    """
    engine = RAGEngine(db)
    return engine.ask(request)
