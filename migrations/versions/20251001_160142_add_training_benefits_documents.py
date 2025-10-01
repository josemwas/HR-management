"""Add training, benefits and documents tables

Revision ID: 20251001_160142
Revises: eab91ad8c8b8
Create Date: 2025-01-01 16:01:42.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20251001_160142'
down_revision = 'eab91ad8c8b8'
branch_labels = None
depends_on = None


def upgrade():
    # Create training_programs table
    op.create_table('training_programs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('trainer', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('duration_hours', sa.Integer(), nullable=True),
    sa.Column('max_participants', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('training_type', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create training_enrollments table
    op.create_table('training_enrollments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('program_id', sa.Integer(), nullable=False),
    sa.Column('enrollment_date', sa.DateTime(), nullable=True),
    sa.Column('completion_status', sa.String(length=20), nullable=True),
    sa.Column('completion_date', sa.DateTime(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('certificate_issued', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['training_programs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create employee_documents table
    op.create_table('employee_documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('document_name', sa.String(length=200), nullable=False),
    sa.Column('document_type', sa.String(length=50), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('mime_type', sa.String(length=100), nullable=True),
    sa.Column('uploaded_by', sa.Integer(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.Column('is_confidential', sa.Boolean(), nullable=True),
    sa.Column('expiry_date', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create employee_benefits table
    op.create_table('employee_benefits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('benefit_type', sa.String(length=50), nullable=False),
    sa.Column('benefit_name', sa.String(length=200), nullable=False),
    sa.Column('provider', sa.String(length=100), nullable=True),
    sa.Column('policy_number', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('premium_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('employer_contribution', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('employee_contribution', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('coverage_details', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('employee_benefits')
    op.drop_table('employee_documents')
    op.drop_table('training_enrollments')
    op.drop_table('training_programs')