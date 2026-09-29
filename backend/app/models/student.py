"""
Student Profile ORM Model
Stores comprehensive student academic and demographic profiles for eligibility evaluation.
"""

from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import Integer, Numeric, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Student(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Student entity representation.
    Captures educational background, financial status, domicile, and interests.
    """

    __tablename__ = "students"

    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    education_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    course: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    year_of_study: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cgpa: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    annual_family_income: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    domicile: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="General", index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    institution_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    academic_interests: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    career_interests: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Indian")

    # Relationship to eligibility check history
    eligibility_logs: Mapped[List["EligibilityCheckLog"]] = relationship(
        "EligibilityCheckLog",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize student model instance into a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "education_level": self.education_level,
            "course": self.course,
            "branch": self.branch,
            "year_of_study": self.year_of_study,
            "semester": self.semester,
            "cgpa": float(self.cgpa) if self.cgpa is not None else None,
            "percentage": float(self.percentage) if self.percentage is not None else None,
            "annual_family_income": (
                float(self.annual_family_income) if self.annual_family_income is not None else None
            ),
            "state": self.state,
            "domicile": self.domicile,
            "category": self.category,
            "gender": self.gender,
            "institution_type": self.institution_type,
            "age": self.age,
            "academic_interests": self.academic_interests or [],
            "career_interests": self.career_interests or [],
            "nationality": self.nationality,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
