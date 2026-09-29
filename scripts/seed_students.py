"""
Student Data Seeder
Populates the database with realistic sample student profiles.
"""

import sys
import os

# Add the backend directory to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.student import Student

SAMPLE_STUDENTS = [
    {
        "name": "Aarav Sharma",
        "education_level": "UG",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year_of_study": 3,
        "semester": 5,
        "cgpa": 8.85,
        "percentage": 85.5,
        "annual_family_income": 250000.0,
        "state": "Maharashtra",
        "domicile": "Maharashtra",
        "category": "OBC",
        "gender": "Male",
        "institution_type": "Government",
        "age": 20,
        "academic_interests": ["Artificial Intelligence", "Distributed Systems"],
        "career_interests": ["Software Engineering"],
        "nationality": "Indian"
    },
    {
        "name": "Priya Patel",
        "education_level": "PG",
        "course": "M.Sc",
        "branch": "Biotechnology",
        "year_of_study": 1,
        "semester": 1,
        "cgpa": 9.1,
        "percentage": 90.0,
        "annual_family_income": 120000.0,
        "state": "Gujarat",
        "domicile": "Gujarat",
        "category": "EWS",
        "gender": "Female",
        "institution_type": "Private",
        "age": 22,
        "academic_interests": ["Genetics", "Bioinformatics"],
        "career_interests": ["Research", "Healthcare"],
        "nationality": "Indian"
    },
    {
        "name": "Rahul Verma",
        "education_level": "Class 12",
        "course": "Science",
        "year_of_study": 1,
        "percentage": 92.5,
        "annual_family_income": 80000.0,
        "state": "Uttar Pradesh",
        "domicile": "Uttar Pradesh",
        "category": "SC",
        "gender": "Male",
        "institution_type": "Government",
        "age": 17,
        "academic_interests": ["Physics", "Mathematics"],
        "career_interests": ["Engineering", "Space Science"],
        "nationality": "Indian"
    }
]

def seed_students():
    """Seed the database with sample students."""
    db: Session = SessionLocal()
    try:
        # Check if students already exist to prevent duplicates
        existing_count = db.query(Student).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing students. Skipping seeding to prevent duplicates.")
            return

        for student_data in SAMPLE_STUDENTS:
            student = Student(**student_data)
            db.add(student)
            
        db.commit()
        print(f"Successfully seeded {len(SAMPLE_STUDENTS)} student profiles!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding students: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting student seeder...")
    seed_students()
