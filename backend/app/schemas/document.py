"""
Source Document and Document Chunk Pydantic Schemas
Defines request and response validation schemas for ingested PDF sources and text chunks.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional
import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SourceCategory(str, Enum):
    NSP = "NSP"
    GOI = "Government of India"
    UGC = "UGC"
    AICTE = "AICTE"


class SourceDocumentBase(BaseModel):
    """Base source document attributes."""

    title: str = Field(..., max_length=255, description="Document title")
    source_category: SourceCategory = Field(..., description="Must be one of the four approved official sources")
    source_organization: str = Field(..., max_length=255, description="Specific issuing body or ministry")
    source_url: Optional[str] = Field(default=None, max_length=500, description="Public official portal URL")
    document_type: str = Field(default="Scholarship Guideline", max_length=100)
    file_path: Optional[str] = Field(default=None, max_length=500)
    academic_year: Optional[str] = Field(default=None, max_length=50)
    publication_date: Optional[date] = None
    last_verified_date: Optional[date] = None
    ingestion_status: str = Field(default="pending", description="pending, ingested, failed")


class SourceDocumentCreate(SourceDocumentBase):
    """Payload for creating or registering a source document."""
    pass


class SourceDocumentResponse(SourceDocumentBase):
    """Response model for a source document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime


class DocumentChunkBase(BaseModel):
    """Base document chunk attributes."""

    source_document_id: uuid.UUID
    content: str
    chunk_index: int
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    chunk_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentChunkResponse(DocumentChunkBase):
    """Response model for a document chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
