"""
Student Profile Pydantic Schemas
Defines request and response validation models for student profiles.
"""

from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    """Base student profile fields."""

    name: Optional[str] = Field(default=None, max_length=255, description="Student full name")
    education_level: str = Field(..., description="e.g. UG, PG, PhD, Class 10, Class 12, Diploma")
    course: str = Field(..., max_length=255, description="e.g. B.Tech, M.Tech, B.Sc, MBBS")
    branch: Optional[str] = Field(default=None, max_length=255, description="Specialization/Department")
    year_of_study: Optional[int] = Field(default=None, ge=1, le=10, description="Current year of study")
    semester: Optional[int] = Field(default=None, ge=1, le=20, description="Current semester")
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0, description="Current CGPA on 10.0 scale")
    percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Academic percentage")
    annual_family_income: Optional[float] = Field(
        default=None, ge=0.0, description="Gross annual family income in INR"
    )
    state: Optional[str] = Field(default=None, max_length=100, description="Current state of residence")
    domicile: Optional[str] = Field(default=None, max_length=100, description="State of permanent domicile")
    category: str = Field(
        default="General",
        description="Reservation category (General, OBC, SC, ST, EWS, Minority, PwD)",
    )
    gender: Optional[str] = Field(default=None, max_length=50, description="Male, Female, Any, Other")
    institution_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Government, Private, Deemed University, Central University",
    )
    age: Optional[int] = Field(default=None, ge=10, le=100, description="Age in years")
    academic_interests: Optional[List[str]] = Field(
        default_factory=list, description="Academic topics of interest"
    )
    career_interests: Optional[List[str]] = Field(
        default_factory=list, description="Career and research goals"
    )
    nationality: Optional[str] = Field(default="Indian", max_length=100)


class StudentCreate(StudentBase):
    """Payload for creating a new student profile."""
    pass


class StudentUpdate(BaseModel):
    """Payload for updating an existing student profile."""

    name: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[str] = None
    branch: Optional[str] = None
    year_of_study: Optional[int] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    percentage: Optional[float] = None
    annual_family_income: Optional[float] = None
    state: Optional[str] = None
    domicile: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    institution_type: Optional[str] = None
    age: Optional[int] = None
    academic_interests: Optional[List[str]] = None
    career_interests: Optional[List[str]] = None
    nationality: Optional[str] = None


class StudentResponse(StudentBase):
    """Response model for a student profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
