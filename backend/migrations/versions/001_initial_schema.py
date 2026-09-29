"""Initial schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-11 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. students
    op.create_table(
        'students',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('education_level', sa.String(length=50), nullable=False),
        sa.Column('course', sa.String(length=255), nullable=False),
        sa.Column('branch', sa.String(length=255), nullable=True),
        sa.Column('year_of_study', sa.Integer(), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('cgpa', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('annual_family_income', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('domicile', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='General'),
        sa.Column('gender', sa.String(length=50), nullable=True),
        sa.Column('institution_type', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('academic_interests', sa.JSON(), nullable=True),
        sa.Column('career_interests', sa.JSON(), nullable=True),
        sa.Column('nationality', sa.String(length=100), nullable=True, server_default='Indian'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_students_education_level', 'students', ['education_level'])
    op.create_index('ix_students_course', 'students', ['course'])
    op.create_index('ix_students_category', 'students', ['category'])
    op.create_index('ix_students_state', 'students', ['state'])

    # 2. source_documents
    op.create_table(
        'source_documents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('document_type', sa.String(length=100), nullable=False, server_default='Scholarship Guideline'),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=True),
        sa.Column('last_verified_date', sa.Date(), nullable=True),
        sa.Column('ingestion_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_source_documents_title', 'source_documents', ['title'])
    op.create_index('ix_source_documents_ingestion_status', 'source_documents', ['ingestion_status'])

    # 3. opportunities
    op.create_table(
        'opportunities',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('opportunity_type', sa.String(length=50), nullable=False),
        sa.Column('education_level', sa.JSON(), nullable=False),
        sa.Column('course', sa.JSON(), nullable=True),
        sa.Column('field_of_study', sa.JSON(), nullable=True),
        sa.Column('minimum_cgpa', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('minimum_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('maximum_income', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('minimum_income', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('age_limit_max', sa.Integer(), nullable=True),
        sa.Column('category', sa.JSON(), nullable=True),
        sa.Column('gender', sa.String(length=50), nullable=True),
        sa.Column('state', sa.JSON(), nullable=True),
        sa.Column('domicile_requirement', sa.String(length=255), nullable=True),
        sa.Column('institution_type', sa.JSON(), nullable=True),
        sa.Column('nationality_requirement', sa.String(length=100), nullable=True, server_default='Indian'),
        sa.Column('benefit_description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('duration', sa.String(length=100), nullable=True),
        sa.Column('opening_date', sa.Date(), nullable=True),
        sa.Column('closing_date', sa.Date(), nullable=True),
        sa.Column('renewal_info', sa.Text(), nullable=True),
        sa.Column('required_documents', sa.JSON(), nullable=True),
        sa.Column('application_process', sa.Text(), nullable=True),
        sa.Column('official_url', sa.String(length=500), nullable=True),
        sa.Column('academic_year', sa.String(length=50), nullable=True),
        sa.Column('last_verified_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('source_document_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['source_document_id'], ['source_documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_opportunities_name', 'opportunities', ['name'])
    op.create_index('ix_opportunities_provider', 'opportunities', ['provider'])
    op.create_index('ix_opportunities_opportunity_type', 'opportunities', ['opportunity_type'])
    op.create_index('ix_opportunities_status', 'opportunities', ['status'])
    op.create_index('ix_opportunities_source_document_id', 'opportunities', ['source_document_id'])

    # 4. document_chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('source_document_id', sa.Uuid(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('chunk_metadata', sa.JSON(), nullable=True),
        sa.Column('embedding_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['source_document_id'], ['source_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_document_chunks_source_document_id', 'document_chunks', ['source_document_id'])
    op.create_index('ix_document_chunks_embedding_id', 'document_chunks', ['embedding_id'])

    # 5. eligibility_check_logs
    op.create_table(
        'eligibility_check_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('opportunity_id', sa.Uuid(), nullable=False),
        sa.Column('overall_status', sa.String(length=50), nullable=False),
        sa.Column('rule_results', sa.JSON(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_eligibility_check_logs_student_id', 'eligibility_check_logs', ['student_id'])
    op.create_index('ix_eligibility_check_logs_opportunity_id', 'eligibility_check_logs', ['opportunity_id'])
    op.create_index('ix_eligibility_check_logs_overall_status', 'eligibility_check_logs', ['overall_status'])
    op.create_index('ix_eligibility_check_logs_checked_at', 'eligibility_check_logs', ['checked_at'])


def downgrade() -> None:
    op.drop_table('eligibility_check_logs')
    op.drop_table('document_chunks')
    op.drop_table('opportunities')
    op.drop_table('source_documents')
    op.drop_table('students')
