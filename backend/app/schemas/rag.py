"""
RAG Pydantic Schemas
Defines request and response validation schemas for Retrieval-Augmented Generation (Q&A).
"""

from typing import List, Optional
import uuid
from pydantic import BaseModel, Field

class SourceAttribution(BaseModel):
    """Provenance data for a retrieved document chunk."""
    
    chunk_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    opportunity_id: Optional[uuid.UUID] = None
    opportunity_name: Optional[str] = None
    similarity_score: Optional[float] = None
    source_title: Optional[str] = None
    page_number: Optional[int] = None
    source_url: Optional[str] = None


class AskRequest(BaseModel):
    """Payload for asking a question."""
    
    query: str = Field(..., description="The user's question.")
    opportunity_id: Optional[uuid.UUID] = Field(None, description="Optional filter to restrict context to a specific scholarship.")
    top_k: Optional[int] = Field(5, gt=0, le=20, description="Number of relevant chunks to retrieve.")


class AnswerResponse(BaseModel):
    """Payload for the generated answer."""
    
    answer: str
    sources: List[SourceAttribution]
