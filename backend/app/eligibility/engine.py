"""
Eligibility Engine
Orchestrates the evaluation of a student profile against opportunity rules.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.eligibility_check_log import EligibilityCheckLog
from app.schemas.eligibility import EligibilityResultSchema, RuleResultSchema
from app.eligibility.rules import AcademicRule, FinancialRule, DemographicRule
from app.core.demo import TEMP_STUDENT_PROFILES

class EligibilityEngine:
    """
    Evaluates a student against one or more opportunities.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rules = [
            AcademicRule(),
            FinancialRule(),
            DemographicRule()
        ]

    def evaluate_opportunity(self, student: Student, opportunity: Opportunity) -> EligibilityResultSchema:
        """
        Evaluate a single opportunity.
        """
        rule_results: List[RuleResultSchema] = []
        overall_status = "ELIGIBLE"
        has_unknown = False
        
        # 1. Execute all rules
        for rule in self.rules:
            result_dict = rule.evaluate(student, opportunity)
            rule_schema = RuleResultSchema(**result_dict)
            rule_results.append(rule_schema)
            
            if rule_schema.result == "FAIL":
                overall_status = "NOT_ELIGIBLE"
            elif rule_schema.result == "UNKNOWN" and overall_status != "NOT_ELIGIBLE":
                has_unknown = True
                
        # 2. Determine final status
        if overall_status != "NOT_ELIGIBLE" and has_unknown:
            overall_status = "INSUFFICIENT_INFORMATION"
            
        # 3. Generate summary
        if overall_status == "ELIGIBLE":
            summary = "Student meets all deterministic criteria for this opportunity."
        elif overall_status == "NOT_ELIGIBLE":
            failed_rules = [r.rule_name for r in rule_results if r.result == "FAIL"]
            summary = f"Student failed the following rules: {', '.join(failed_rules)}."
        else:
            unknown_rules = [r.rule_name for r in rule_results if r.result == "UNKNOWN"]
            summary = f"Insufficient information to determine eligibility for: {', '.join(unknown_rules)}."
            
        # 4. Save audit log to DB (ignore for demo students not in DB)
        log = EligibilityCheckLog(
            student_id=student.id,
            opportunity_id=opportunity.id,
            overall_status=overall_status,
            rule_results=[r.model_dump() for r in rule_results],
            summary=summary
        )
        try:
            self.db.add(log)
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        # 5. Return structured result
        return EligibilityResultSchema(
            opportunity_id=opportunity.id,
            overall_status=overall_status,
            rule_results=rule_results,
            summary=summary
        )

    def evaluate_multiple(self, student: Student, opportunities: List[Opportunity]) -> List[EligibilityResultSchema]:
        """
        Evaluate a list of opportunities.
        """
        results = []
        for opp in opportunities:
            results.append(self.evaluate_opportunity(student, opp))
        return results
