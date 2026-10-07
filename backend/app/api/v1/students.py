"""
Students API Router
Handles CRUD operations for Student profiles.
"""

from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, pagination_params
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.core.demo import TEMP_STUDENT_PROFILES
from pydantic import BaseModel
from datetime import datetime

class DemoProfileRequest(BaseModel):
    temporary_session_id: str
    profile: StudentCreate

router = APIRouter()

@router.post("/demo")
def store_demo_profile(request: DemoProfileRequest):
    """LOCAL DEMO MODE: Store student profile in-memory only."""
    TEMP_STUDENT_PROFILES[request.temporary_session_id] = request.profile.model_dump()
    return {"status": "success", "session_id": request.temporary_session_id}


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    *,
    db: Session = Depends(get_db),
    student_in: StudentCreate,
) -> Any:
    """Create a new student profile."""
    student = Student(**student_in.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=List[StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params)
) -> Any:
    """Retrieve all student profiles."""
    return db.query(Student).offset(params["skip"]).limit(params["limit"]).all()


@router.get("/{id}", response_model=StudentResponse)
def get_student(
    id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Retrieve a specific student profile by ID."""
    if id in TEMP_STUDENT_PROFILES:
        student_data = TEMP_STUDENT_PROFILES[id]
        
        try:
            parsed_id = uuid.UUID(id)
        except ValueError:
            parsed_id = uuid.uuid4()
            
        return StudentResponse(
            id=parsed_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **student_data
        )

    try:
        parsed_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Student not found")

    student = db.query(Student).filter(Student.id == parsed_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{id}", response_model=StudentResponse)
def update_student(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
    student_in: StudentUpdate,
) -> Any:
    """Update an existing student profile."""
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    update_data = student_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
        
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{id}", response_model=dict)
def delete_student(
    id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Delete a student profile."""
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}
