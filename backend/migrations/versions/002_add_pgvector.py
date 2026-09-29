"""add pgvector and embeddings

Revision ID: 002_add_pgvector
Revises: 001_initial_schema
Create Date: 2026-09-29 17:37:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '002_add_pgvector'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable the pgvector extension in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Add embedding column, remove embedding_id
    op.add_column('document_chunks', sa.Column('embedding', Vector(384), nullable=True))
    op.drop_index('ix_document_chunks_embedding_id', table_name='document_chunks')
    op.drop_column('document_chunks', 'embedding_id')


def downgrade() -> None:
    # Re-add embedding_id and remove embedding
    op.add_column('document_chunks', sa.Column('embedding_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_index('ix_document_chunks_embedding_id', 'document_chunks', ['embedding_id'], unique=False)
    op.drop_column('document_chunks', 'embedding')
    
    # Drop vector extension (optional, usually safer to leave it unless specifically required)
    # op.execute("DROP EXTENSION IF EXISTS vector;")
