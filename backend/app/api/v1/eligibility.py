"""
Eligibility API Router
Exposes the deterministic eligibility engine.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse
from app.eligibility.engine import EligibilityEngine
from app.core.demo import TEMP_STUDENT_PROFILES
from datetime import datetime

router = APIRouter()

@router.post("/evaluate", response_model=EligibilityCheckResponse)
def evaluate_eligibility(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Evaluates a student's eligibility against specified opportunities.
    If opportunity_ids is omitted or empty, it evaluates against ALL active opportunities.
    """
    if request.student_id in TEMP_STUDENT_PROFILES:
        profile_data = TEMP_STUDENT_PROFILES[request.student_id]
        student = Student(**profile_data)
        try:
            parsed_id = uuid.UUID(request.student_id)
        except ValueError:
            parsed_id = uuid.uuid4()
        student.id = parsed_id
        student.created_at = datetime.utcnow()
        student.updated_at = datetime.utcnow()
    else:
        try:
            parsed_id = uuid.UUID(request.student_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Student not found")
            
        student = db.query(Student).filter(Student.id == parsed_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
    if request.opportunity_ids:
        opportunities = db.query(Opportunity).filter(Opportunity.id.in_(request.opportunity_ids)).all()
        if not opportunities:
            raise HTTPException(status_code=404, detail="None of the specified opportunities were found")
    else:
        opportunities = db.query(Opportunity).filter(Opportunity.status == "Active").all()
        
    engine = EligibilityEngine(db)
    evaluations = engine.evaluate_multiple(student, opportunities)
    
    return EligibilityCheckResponse(
        student_id=student.id,
        evaluations=evaluations
    )
