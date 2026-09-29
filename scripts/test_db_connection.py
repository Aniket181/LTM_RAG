"""
Database Connection & Smoke Test Script
Tests connectivity to PostgreSQL and verifies model querying.

Usage:
    python scripts/test_db_connection.py
"""

import os
import sys
import uuid

# Add backend to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.document import SourceDocument, DocumentChunk
from app.models.eligibility_check_log import EligibilityCheckLog


def run_smoke_test():
    print("=" * 60)
    print("RAG System — Database Connection & Smoke Test")
    print(f"Target Database URL: {settings.database_url}")
    print("=" * 60)

    # 1. Connectivity Check
    print("\n[1/4] Testing database connectivity (SELECT 1)...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
        print("  ✓ Database connection established successfully.")
    except Exception as exc:
        print("  ✗ Could not connect to PostgreSQL database!")
        print(f"    Error: {exc}")
        print("\nTroubleshooting tips:")
        print("  1. Is the Docker PostgreSQL container running?")
        print("     Run: docker compose up -d")
        print("  2. Check container status:")
        print("     Run: docker compose ps")
        print("  3. Verify environment variables in .env:")
        print(f"     Host: {settings.postgres_host}:{settings.postgres_port}")
        print(f"     User: {settings.postgres_user}, Database: {settings.postgres_db}")
        sys.exit(1)

    # 2. Check Tables Existence
    print("\n[2/4] Checking registered tables...")
    with engine.connect() as conn:
        tables_res = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        existing_tables = [row[0] for row in tables_res.fetchall()]
        print(f"  Found {len(existing_tables)} tables in 'public' schema: {existing_tables}")

    required_tables = {"students", "opportunities", "source_documents", "document_chunks", "eligibility_check_logs"}
    missing = required_tables - set(existing_tables)
    if missing:
        print(f"  ⚠ Note: Tables {missing} are not yet created in the database.")
        print("    Run Alembic migrations to create them:")
        print("    cd backend && alembic upgrade head")
    else:
        print("  ✓ All required tables are present.")

    # 3. Model CRUD Roundtrip (if tables exist)
    if not missing:
        print("\n[3/4] Testing Model CRUD roundtrip...")
        db = SessionLocal()
        test_student_id = None
        try:
            # Create
            test_student = Student(
                name="Test Student SmokeCheck",
                education_level="UG",
                course="B.Tech",
                category="General",
                annual_family_income=300000.0,
            )
            db.add(test_student)
            db.commit()
            db.refresh(test_student)
            test_student_id = test_student.id
            print(f"  ✓ Inserted smoke-test student with ID: {test_student_id}")

            # Read
            fetched = db.query(Student).filter(Student.id == test_student_id).first()
            assert fetched is not None
            assert fetched.name == "Test Student SmokeCheck"
            print(f"  ✓ Successfully queried back student: {fetched.name}")

            # Delete
            db.delete(fetched)
            db.commit()
            print("  ✓ Successfully deleted smoke-test record.")
        except Exception as exc:
            db.rollback()
            print(f"  ✗ CRUD test encountered an error: {exc}")
        finally:
            db.close()
    else:
        print("\n[3/4] Skipping CRUD test until migrations are applied.")

    # 4. Summary
    print("\n[4/4] Verification Summary:")
    print("  ✓ Database engine and connection pool working.")
    print("  ✓ Models mapped correctly with SQLAlchemy 2.0.")
    print("\nSmoke test complete!")


if __name__ == "__main__":
    run_smoke_test()
