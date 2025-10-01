"""Add SaaS multi-tenancy support

Revision ID: saas_migration_001
Revises: eab91ad8c8b8
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import date, timedelta

# revision identifiers, used by Alembic.
revision = 'saas_migration_001'
down_revision = 'eab91ad8c8b8'
branch_labels = None
depends_on = None

def upgrade():
    # Create subscription_plans table
    op.create_table('subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly', sa.Float(), nullable=True),
        sa.Column('price_yearly', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('employee_limit', sa.Integer(), nullable=True),
        sa.Column('storage_limit_gb', sa.Integer(), nullable=True),
        sa.Column('api_calls_per_month', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_popular', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('trial_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('subscription_status', sa.String(length=20), nullable=True),
        sa.Column('trial_start_date', sa.Date(), nullable=True),
        sa.Column('trial_end_date', sa.Date(), nullable=True),
        sa.Column('subscription_start_date', sa.Date(), nullable=True),
        sa.Column('subscription_end_date', sa.Date(), nullable=True),
        sa.Column('employee_limit', sa.Integer(), nullable=True),
        sa.Column('current_employee_count', sa.Integer(), nullable=True),
        sa.Column('storage_limit_gb', sa.Integer(), nullable=True),
        sa.Column('current_storage_gb', sa.Float(), nullable=True),
        sa.Column('billing_email', sa.String(length=120), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=True),
        sa.Column('payment_method_id', sa.String(length=100), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('date_format', sa.String(length=20), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('enable_two_factor', sa.Boolean(), nullable=True),
        sa.Column('password_policy', sa.JSON(), nullable=True),
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('slug')
    )

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('billing_cycle', sa.String(length=10), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('next_billing_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create invoices table
    op.create_table('invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('billing_period_start', sa.Date(), nullable=False),
        sa.Column('billing_period_end', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('stripe_invoice_id', sa.String(length=100), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )

    # Create usage_logs table
    op.create_table('usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('recorded_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add organization_id to existing tables
    op.add_column('employees', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('departments', sa.Column('organization_id', sa.Integer(), nullable=True))

    # Create foreign key constraints for organization_id
    op.create_foreign_key(None, 'employees', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key(None, 'departments', 'organizations', ['organization_id'], ['id'])

    # Drop the old unique constraints and create new ones scoped to organization
    op.drop_constraint('uq_employee_employee_id', 'employees', type_='unique')
    op.drop_constraint('uq_employee_email', 'employees', type_='unique')
    op.drop_constraint('uq_department_name', 'departments', type_='unique')

    # Create new unique constraints within organization scope
    op.create_unique_constraint('uq_org_employee_id', 'employees', ['organization_id', 'employee_id'])
    op.create_unique_constraint('uq_org_email', 'employees', ['organization_id', 'email'])
    op.create_unique_constraint('uq_org_dept_name', 'departments', ['organization_id', 'name'])


def downgrade():
    # Drop new unique constraints
    op.drop_constraint('uq_org_employee_id', 'employees', type_='unique')
    op.drop_constraint('uq_org_email', 'employees', type_='unique')
    op.drop_constraint('uq_org_dept_name', 'departments', type_='unique')

    # Recreate old unique constraints
    op.create_unique_constraint('uq_employee_employee_id', 'employees', ['employee_id'])
    op.create_unique_constraint('uq_employee_email', 'employees', ['email'])
    op.create_unique_constraint('uq_department_name', 'departments', ['name'])

    # Drop foreign key constraints
    op.drop_constraint(None, 'employees', type_='foreignkey')
    op.drop_constraint(None, 'departments', type_='foreignkey')

    # Remove organization_id columns
    op.drop_column('departments', 'organization_id')
    op.drop_column('employees', 'organization_id')

    # Drop SaaS tables
    op.drop_table('usage_logs')
    op.drop_table('invoices')
    op.drop_table('subscriptions')
    op.drop_table('organizations')
    op.drop_table('subscription_plans')