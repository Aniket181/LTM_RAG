"""
Document and Chunk ORM Models
Represents ingested source guideline PDFs and segmented text chunks for RAG retrieval.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
from pgvector.sqlalchemy import Vector

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class SourceDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Source document representing an official scholarship guideline, policy PDF, or scheme brochure.
    """

    __tablename__ = "source_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Scholarship Guideline")
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    academic_year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_verified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ingestion_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)

    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="source_document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index",
    )
    opportunities: Mapped[List["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="source_document",
    )

    @property
    def chunk_count(self) -> int:
        """Dynamically compute chunk count for Pydantic serialization."""
        return len(self.chunks) if self.chunks is not None else 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize source document into a dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "source_url": self.source_url,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "academic_year": self.academic_year,
            "last_verified_date": self.last_verified_date.isoformat() if self.last_verified_date else None,
            "ingestion_status": self.ingestion_status,
            "chunk_count": len(self.chunks) if self.chunks else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DocumentChunk(Base, UUIDPrimaryKeyMixin):
    """
    Chunked passage from a source document used for semantic retrieval and context assembly.
    """

    __tablename__ = "document_chunks"

    source_document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Semantic Search Embedding
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(384), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    source_document: Mapped["SourceDocument"] = relationship(
        "SourceDocument",
        back_populates="chunks",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize document chunk into a dictionary."""
        return {
            "id": str(self.id),
            "source_document_id": str(self.source_document_id),
            "content": self.content,
            "chunk_index": self.chunk_index,
            "section_title": self.section_title,
            "page_number": self.page_number,
            "chunk_metadata": self.chunk_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
