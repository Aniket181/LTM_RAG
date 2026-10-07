"""add provenance fields

Revision ID: 003_add_provenance_fields
Revises: 002_add_pgvector
Create Date: 2026-10-07 23:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_provenance_fields'
down_revision: Union[str, None] = '002_add_pgvector'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns in a migration-safe manner (nullable first)
    op.add_column('source_documents', sa.Column('source_category', sa.String(length=100), nullable=True))
    op.add_column('source_documents', sa.Column('source_organization', sa.String(length=255), nullable=True))
    op.add_column('source_documents', sa.Column('publication_date', sa.Date(), nullable=True))
    
    # 2. Explicitly handle existing Phase A-F legacy data
    # Assign them to 'Government of India' category and flag the organization so they can be manually reviewed.
    op.execute(
        "UPDATE source_documents SET "
        "source_category = 'Government of India', "
        "source_organization = 'NEEDS_MANUAL_REVIEW_LEGACY_DATA' "
        "WHERE source_category IS NULL"
    )
    
    # 3. Establish the final NOT NULL constraint now that existing records are valid
    op.alter_column('source_documents', 'source_category', existing_type=sa.String(length=100), nullable=False)
    op.alter_column('source_documents', 'source_organization', existing_type=sa.String(length=255), nullable=False)


def downgrade() -> None:
    op.drop_column('source_documents', 'publication_date')
    op.drop_column('source_documents', 'source_organization')
    op.drop_column('source_documents', 'source_category')
