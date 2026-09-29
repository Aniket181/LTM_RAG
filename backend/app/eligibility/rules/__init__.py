"""
Eligibility Rule Evaluators
Defines the base interface and specific deterministic rules for checking student eligibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.models.student import Student
from app.models.opportunity import Opportunity


class Rule(ABC):
    """Base class for eligibility rules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the rule."""
        pass

    @abstractmethod
    def evaluate(self, student: Student, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Evaluate the rule.
        Returns a dictionary matching RuleResultSchema:
        {
            "rule_name": str,
            "condition": str,
            "student_value": Any,
            "required_value": str,
            "result": "PASS" | "FAIL" | "WARN" | "UNKNOWN",
            "detail": str
        }
        """
        pass


class AcademicRule(Rule):
    """Evaluates education level, course, and minimum percentage/CGPA requirements."""
    
    @property
    def name(self) -> str:
        return "AcademicRule"

    def evaluate(self, student: Student, opportunity: Opportunity) -> Dict[str, Any]:
        result = "PASS"
        details = []
        
        # Check Education Level
        if opportunity.education_level:
            if student.education_level not in opportunity.education_level:
                result = "FAIL"
                details.append(f"Education level '{student.education_level}' not in required {opportunity.education_level}")
        
        # Check Course
        if opportunity.course:
            if student.course not in opportunity.course:
                result = "FAIL"
                details.append(f"Course '{student.course}' not in required {opportunity.course}")
                
        # Check Minimum Percentage
        if opportunity.minimum_percentage is not None:
            # Try to compare percentage, then CGPA
            student_val = None
            if student.percentage is not None:
                student_val = float(student.percentage)
            elif student.cgpa is not None:
                # Rough conversion if percentage is missing
                student_val = float(student.cgpa) * 9.5
                
            if student_val is None:
                if result != "FAIL":
                    result = "UNKNOWN"
                details.append("Missing student academic percentage/CGPA")
            elif student_val < float(opportunity.minimum_percentage):
                result = "FAIL"
                details.append(f"Academic score {student_val} < required {opportunity.minimum_percentage}")
                
        detail_str = "; ".join(details) if details else "Academic criteria met."
        
        return {
            "rule_name": self.name,
            "condition": "education_level, course, minimum_percentage",
            "student_value": f"{student.education_level}, {student.course}, {student.percentage or student.cgpa}",
            "required_value": f"{opportunity.education_level}, {opportunity.course}, {opportunity.minimum_percentage}",
            "result": result,
            "detail": detail_str
        }


class FinancialRule(Rule):
    """Evaluates family income constraints."""
    
    @property
    def name(self) -> str:
        return "FinancialRule"

    def evaluate(self, student: Student, opportunity: Opportunity) -> Dict[str, Any]:
        if opportunity.maximum_income is None:
            return {
                "rule_name": self.name,
                "condition": "maximum_income",
                "student_value": float(student.annual_family_income) if student.annual_family_income else None,
                "required_value": "None",
                "result": "PASS",
                "detail": "No maximum income requirement."
            }
            
        if student.annual_family_income is None:
            return {
                "rule_name": self.name,
                "condition": "maximum_income",
                "student_value": None,
                "required_value": f"<= {opportunity.maximum_income}",
                "result": "UNKNOWN",
                "detail": "Missing annual family income."
            }
            
        student_income = float(student.annual_family_income)
        req_income = float(opportunity.maximum_income)
        
        if student_income <= req_income:
            return {
                "rule_name": self.name,
                "condition": "maximum_income",
                "student_value": student_income,
                "required_value": f"<= {req_income}",
                "result": "PASS",
                "detail": "Income requirement met."
            }
        else:
            return {
                "rule_name": self.name,
                "condition": "maximum_income",
                "student_value": student_income,
                "required_value": f"<= {req_income}",
                "result": "FAIL",
                "detail": f"Income {student_income} exceeds maximum {req_income}."
            }


class DemographicRule(Rule):
    """Evaluates category, gender, and state domicile requirements."""
    
    @property
    def name(self) -> str:
        return "DemographicRule"

    def evaluate(self, student: Student, opportunity: Opportunity) -> Dict[str, Any]:
        result = "PASS"
        details = []
        
        # Check Category
        if opportunity.category:
            if "Any" not in opportunity.category and "All" not in opportunity.category:
                if student.category not in opportunity.category:
                    result = "FAIL"
                    details.append(f"Category '{student.category}' not in required {opportunity.category}")
                    
        # Check Gender
        if opportunity.gender and opportunity.gender.lower() not in ["any", "all"]:
            if student.gender != opportunity.gender:
                result = "FAIL"
                details.append(f"Gender '{student.gender}' does not match required '{opportunity.gender}'")

        # Check State Domicile
        if opportunity.state and opportunity.state.lower() not in ["any", "all", "national", "india"]:
            if student.domicile != opportunity.state:
                result = "FAIL"
                details.append(f"Domicile '{student.domicile}' does not match required '{opportunity.state}'")
                
        detail_str = "; ".join(details) if details else "Demographic criteria met."
        
        return {
            "rule_name": self.name,
            "condition": "category, gender, state",
            "student_value": f"{student.category}, {student.gender}, {student.domicile}",
            "required_value": f"{opportunity.category}, {opportunity.gender}, {opportunity.state}",
            "result": result,
            "detail": detail_str
        }
