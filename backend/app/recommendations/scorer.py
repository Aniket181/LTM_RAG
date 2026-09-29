"""
Recommendation Scoring Components
Determines deterministic, transparent scores for ranking opportunities.
"""

from datetime import date
from typing import Dict, Any, List
from app.models.student import Student
from app.models.opportunity import Opportunity

class Scorer:
    """Base interface for all scorers."""
    def score(self, student: Student, opportunity: Opportunity, reference_date: date = None) -> Dict[str, Any]:
        pass

class DeadlineScorer(Scorer):
    """
    Scores an opportunity based on its upcoming deadline urgency.
    Score table:
    - missing or expired: 0
    - 0-7 days: 25
    - 8-30 days: 20
    - 31-90 days: 15
    - 91-180 days: 10
    - >180 days: 5
    """
    def score(self, student: Student, opportunity: Opportunity, reference_date: date = None) -> Dict[str, Any]:
        if opportunity.closing_date is None:
            return {"score": 0, "reason": "No closing deadline specified."}
            
        ref_date = reference_date or date.today()
        days_remaining = (opportunity.closing_date - ref_date).days
        
        if days_remaining < 0:
            return {"score": 0, "reason": f"Deadline expired {abs(days_remaining)} days ago."}
        elif days_remaining <= 7:
            return {"score": 25, "reason": f"Deadline is extremely urgent (in {days_remaining} days)."}
        elif days_remaining <= 30:
            return {"score": 20, "reason": f"Deadline is approaching (in {days_remaining} days)."}
        elif days_remaining <= 90:
            return {"score": 15, "reason": f"Deadline is within 3 months."}
        elif days_remaining <= 180:
            return {"score": 10, "reason": f"Deadline is within 6 months."}
        else:
            return {"score": 5, "reason": f"Deadline is far in the future."}

class FinancialNeedScorer(Scorer):
    """
    Scores need-based opportunities.
    If opportunity has maximum_income, we assume it's need-based.
    Lower family income scores higher, up to 20 points.
    """
    def score(self, student: Student, opportunity: Opportunity, reference_date: date = None) -> Dict[str, Any]:
        if opportunity.maximum_income is None:
            return {"score": 0, "reason": "Opportunity is not explicitly need-based."}
            
        if student.annual_family_income is None:
            return {"score": 0, "reason": "Student family income is unknown."}
            
        student_income = float(student.annual_family_income)
        max_income = float(opportunity.maximum_income)
        
        if student_income > max_income:
            return {"score": 0, "reason": "Student income exceeds the maximum threshold."}
            
        # Give more points the further below the maximum threshold they are
        # Formula: (1 - (student_income / max_income)) * 20
        ratio = student_income / max_income if max_income > 0 else 1.0
        bonus = int((1.0 - ratio) * 20)
        
        return {"score": bonus, "reason": f"Awarded {bonus} points for financial need alignment."}

class AcademicMeritScorer(Scorer):
    """
    Scores academic merit above the minimum threshold.
    Up to 25 points based on margin.
    """
    def score(self, student: Student, opportunity: Opportunity, reference_date: date = None) -> Dict[str, Any]:
        score = 0
        reason = "No explicit academic merit bonus."
        
        # Determine based on percentage or CGPA
        if opportunity.minimum_percentage is not None and student.percentage is not None:
            min_p = float(opportunity.minimum_percentage)
            stu_p = float(student.percentage)
            if stu_p >= min_p:
                margin = stu_p - min_p
                # Max 25 points for 25%+ margin
                bonus = min(25, int(margin))
                score = bonus
                reason = f"Academic performance exceeds requirement by {margin:.1f}%."
                
        elif opportunity.minimum_cgpa is not None and student.cgpa is not None:
            min_c = float(opportunity.minimum_cgpa)
            stu_c = float(student.cgpa)
            if stu_c >= min_c:
                margin = stu_c - min_c
                # Max 25 points for 2.5+ CGPA margin (roughly x10 scaling to match percentage)
                bonus = min(25, int(margin * 10))
                score = bonus
                reason = f"Academic performance exceeds requirement by {margin:.2f} CGPA."
                
        return {"score": score, "reason": reason}

class DemographicMatchScorer(Scorer):
    """
    Scores precise demographic matches if the opportunity is targeted.
    Max 30 points.
    """
    def score(self, student: Student, opportunity: Opportunity, reference_date: date = None) -> Dict[str, Any]:
        score = 0
        reasons = []
        
        # State Match (+10)
        if opportunity.state and "Any" not in opportunity.state and "All" not in opportunity.state and "India" not in opportunity.state:
            if student.domicile in opportunity.state or student.state in opportunity.state:
                score += 10
                reasons.append("State domicile explicitly matches the target demographic.")
                
        # Category Match (+10)
        if opportunity.category and "Any" not in opportunity.category and "All" not in opportunity.category:
            if student.category in opportunity.category:
                score += 10
                reasons.append("Category explicitly matches the target demographic.")
                
        # Gender Match (+5)
        if opportunity.gender and opportunity.gender.lower() not in ["any", "all"]:
            if student.gender == opportunity.gender:
                score += 5
                reasons.append("Gender explicitly matches the target demographic.")
                
        # Nationality Match (+5)
        if opportunity.nationality_requirement and opportunity.nationality_requirement.lower() not in ["any", "all", "indian"]:
            if student.nationality == opportunity.nationality_requirement:
                score += 5
                reasons.append("Nationality explicitly matches the target demographic.")
                
        reason_str = " ".join(reasons) if reasons else "Opportunity has broad demographics; no specific bonus awarded."
        
        return {"score": score, "reason": reason_str}
