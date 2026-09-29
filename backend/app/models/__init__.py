"""
Models Package
Central registry of all SQLAlchemy ORM models for the RAG Scholarship Intelligence System.
Importing this package registers all models with Base.metadata.
"""

from app.db.base import Base
from app.models.document import DocumentChunk, SourceDocument
from app.models.eligibility_check_log import EligibilityCheckLog
from app.models.opportunity import Opportunity
from app.models.student import Student

__all__ = [
    "Base",
    "Student",
    "Opportunity",
    "SourceDocument",
    "DocumentChunk",
    "EligibilityCheckLog",
]
