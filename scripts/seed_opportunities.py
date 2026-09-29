"""
Opportunity Data Seeder
Populates the PostgreSQL database with 8 real-world scholarship schemes to test the RAG and eligibility engine.
Run via: python scripts/seed_opportunities.py
"""

import os
import sys
from datetime import date

# Add backend directory to sys.path so app modules can be imported
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

from app.db.session import SessionLocal
from app.models.opportunity import Opportunity

# 8 Real-world scholarship schemes
MOCK_OPPORTUNITIES = [
    {
        "name": "Central Sector Scheme of Scholarship for College and University Students (CSSS)",
        "provider": "Ministry of Education, Government of India",
        "description": "Financial assistance to meritorious students from low-income families to meet a part of their day-to-day expenses while pursuing higher studies.",
        "opportunity_type": "Scholarship",
        "education_level": ["UG", "PG"],
        "course": ["B.Tech", "B.Sc", "B.Com", "BA", "MBBS"],
        "minimum_percentage": 80.0,
        "maximum_income": 450000.0,
        "category": ["General", "OBC", "SC", "ST", "EWS"],
        "gender": "Any",
        "state": [],
        "institution_type": ["Government", "Private"],
        "amount": 12000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://scholarships.gov.in/",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "AICTE Pragati Scholarship for Girls",
        "provider": "All India Council for Technical Education (AICTE)",
        "description": "Scholarship for girl students pursuing technical education (degree/diploma). Maximum two girls per family.",
        "opportunity_type": "Scholarship",
        "education_level": ["UG", "Diploma"],
        "course": ["B.Tech", "B.E.", "Diploma in Engineering"],
        "maximum_income": 800000.0,
        "category": ["General", "OBC", "SC", "ST", "EWS", "Minority"],
        "gender": "Female",
        "institution_type": ["Government", "Private", "Deemed University"],
        "amount": 50000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://www.aicte-india.org/schemes/students-development-schemes/Pragati",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "AICTE Saksham Scholarship for Specially Abled Students",
        "provider": "All India Council for Technical Education (AICTE)",
        "description": "Scholarship for specially-abled students pursuing technical education to promote equity and inclusion.",
        "opportunity_type": "Scholarship",
        "education_level": ["UG", "Diploma"],
        "maximum_income": 800000.0,
        "category": ["PwD"],
        "gender": "Any",
        "institution_type": ["Government", "Private", "Deemed University"],
        "amount": 50000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "Prime Minister's Scholarship Scheme (PMSS)",
        "provider": "Kendriya Sainik Board (KSB), Ministry of Defence",
        "description": "Scholarship for dependent wards and widows of Ex-Servicemen (ESM) and Ex-Coast Guard personnel.",
        "opportunity_type": "Scholarship",
        "education_level": ["UG", "PG"],
        "minimum_percentage": 60.0,
        "category": ["General", "OBC", "SC", "ST"],
        "gender": "Any",
        "amount": 36000.0,  # 3000 pm for girls, 2500 pm for boys (averaging/approx here)
        "duration": "Annual",
        "status": "Active",
        "official_url": "http://ksb.gov.in/PMSS.htm",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "Post Matric Scholarship Scheme for Minorities",
        "provider": "Ministry of Minority Affairs",
        "description": "Awarded to meritorious students from minority communities to pursue higher education from Class 11 to Ph.D.",
        "opportunity_type": "Scholarship",
        "education_level": ["Class 11", "Class 12", "UG", "PG", "PhD", "Diploma"],
        "minimum_percentage": 50.0,
        "maximum_income": 200000.0,
        "category": ["Minority"],
        "gender": "Any",
        "amount": 10000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://scholarships.gov.in/",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "UGC Indira Gandhi Scholarship for Single Girl Child",
        "provider": "University Grants Commission (UGC)",
        "description": "Supports postgraduate education for single girl children in non-professional courses.",
        "opportunity_type": "Scholarship",
        "education_level": ["PG"],
        "age_limit_max": 30,
        "category": ["General", "OBC", "SC", "ST", "EWS", "Minority"],
        "gender": "Female",
        "amount": 36200.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://www.ugc.ac.in/",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "INSPIRE Scholarship for Higher Education (SHE)",
        "provider": "Department of Science & Technology (DST)",
        "description": "Scholarship for top 1% state/central board students pursuing B.Sc./M.Sc. in Basic and Natural Sciences.",
        "opportunity_type": "Fellowship",
        "education_level": ["UG", "PG"],
        "course": ["B.Sc", "M.Sc", "Integrated M.Sc"],
        "field_of_study": ["Basic Sciences", "Natural Sciences"],
        "age_limit_max": 22,
        "gender": "Any",
        "amount": 80000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://online-inspire.gov.in/",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
    {
        "name": "Post Matric Scholarship for SC Students",
        "provider": "Ministry of Social Justice and Empowerment",
        "description": "Financial assistance to Scheduled Caste students studying at post-matriculation or post-secondary stage.",
        "opportunity_type": "Scholarship",
        "education_level": ["Class 11", "Class 12", "UG", "PG", "PhD", "Diploma"],
        "maximum_income": 250000.0,
        "category": ["SC"],
        "gender": "Any",
        "amount": 12000.0,
        "duration": "Annual",
        "status": "Active",
        "official_url": "https://scholarships.gov.in/",
        "academic_year": "2025-2026",
        "last_verified_date": date.today(),
    },
]

def run_seeder():
    print("=" * 60)
    print("Seeding Opportunities into Database")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        added_count = 0
        skipped_count = 0
        
        for opp_data in MOCK_OPPORTUNITIES:
            # Check if opportunity already exists by name
            existing = db.query(Opportunity).filter(Opportunity.name == opp_data["name"]).first()
            if existing:
                print(f"  [SKIP] '{opp_data['name']}' already exists.")
                skipped_count += 1
            else:
                new_opp = Opportunity(**opp_data)
                db.add(new_opp)
                print(f"  [ADD]  '{opp_data['name']}' added.")
                added_count += 1
                
        if added_count > 0:
            db.commit()
            
        print("-" * 60)
        print(f"Seeding complete. Added: {added_count}, Skipped: {skipped_count}.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()
