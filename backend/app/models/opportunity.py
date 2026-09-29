"""
Opportunity ORM Model
Represents scholarship, fellowship, grant, and education opportunity schemes with rich eligibility criteria.
"""

from datetime import date
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Opportunity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Opportunity entity representation.
    Holds official scheme metadata, eligibility constraints, financial benefits, and deadlines.
    """

    __tablename__ = "opportunities"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    education_level: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    course: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    field_of_study: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    minimum_cgpa: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    minimum_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    maximum_income: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    minimum_income: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    age_limit_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    domicile_requirement: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    institution_type: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    nationality_requirement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Indian")
    benefit_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    opening_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    closing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renewal_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_documents: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    application_process: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    academic_year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_verified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active", index=True)

    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    source_document: Mapped[Optional["SourceDocument"]] = relationship(
        "SourceDocument",
        back_populates="opportunities",
    )
    eligibility_logs: Mapped[List["EligibilityCheckLog"]] = relationship(
        "EligibilityCheckLog",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize opportunity into dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "provider": self.provider,
            "description": self.description,
            "opportunity_type": self.opportunity_type,
            "education_level": self.education_level or [],
            "course": self.course or [],
            "field_of_study": self.field_of_study or [],
            "minimum_cgpa": float(self.minimum_cgpa) if self.minimum_cgpa is not None else None,
            "minimum_percentage": float(self.minimum_percentage) if self.minimum_percentage is not None else None,
            "maximum_income": float(self.maximum_income) if self.maximum_income is not None else None,
            "minimum_income": float(self.minimum_income) if self.minimum_income is not None else None,
            "age_limit_max": self.age_limit_max,
            "category": self.category or [],
            "gender": self.gender,
            "state": self.state or [],
            "domicile_requirement": self.domicile_requirement,
            "institution_type": self.institution_type or [],
            "nationality_requirement": self.nationality_requirement,
            "benefit_description": self.benefit_description,
            "amount": float(self.amount) if self.amount is not None else None,
            "duration": self.duration,
            "opening_date": self.opening_date.isoformat() if self.opening_date else None,
            "closing_date": self.closing_date.isoformat() if self.closing_date else None,
            "renewal_info": self.renewal_info,
            "required_documents": self.required_documents or [],
            "application_process": self.application_process,
            "official_url": self.official_url,
            "academic_year": self.academic_year,
            "last_verified_date": self.last_verified_date.isoformat() if self.last_verified_date else None,
            "status": self.status,
            "source_document_id": str(self.source_document_id) if self.source_document_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
