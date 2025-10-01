from datetime import datetime, date
from app import db

class Organization(db.Model):
    """Multi-tenant organization model for SaaS"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)  # subdomain
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # 1-10, 11-50, 51-200, 201-1000, 1000+
    
    # SaaS specific fields
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'))
    subscription_status = db.Column(db.String(20), default='trial')  # trial, active, suspended, cancelled
    trial_start_date = db.Column(db.Date, default=date.today)
    trial_end_date = db.Column(db.Date)
    subscription_start_date = db.Column(db.Date)
    subscription_end_date = db.Column(db.Date)
    
    # Usage limits and tracking
    employee_limit = db.Column(db.Integer, default=5)  # Based on plan
    current_employee_count = db.Column(db.Integer, default=0)
    storage_limit_gb = db.Column(db.Integer, default=1)  # Based on plan
    current_storage_gb = db.Column(db.Float, default=0.0)
    
    # Billing information
    billing_email = db.Column(db.String(120))
    billing_address = db.Column(db.Text)
    payment_method_id = db.Column(db.String(100))  # Stripe customer ID
    
    # Settings and customization
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#007bff')  # Brand color
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='YYYY-MM-DD')
    currency = db.Column(db.String(3), default='USD')
    
    # Security settings
    enable_two_factor = db.Column(db.Boolean, default=False)
    password_policy = db.Column(db.JSON)  # Store password requirements
    session_timeout_minutes = db.Column(db.Integer, default=480)  # 8 hours
    
    # Feature control settings (managed by super admin)
    feature_settings = db.Column(db.JSON)  # Store enabled/disabled features
    suspension_reason = db.Column(db.Text)
    suspended_at = db.Column(db.DateTime)
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = db.relationship('SubscriptionPlan', back_populates='organizations')
    employees = db.relationship('Employee', back_populates='organization', cascade='all, delete-orphan')
    departments = db.relationship('Department', back_populates='organization', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', back_populates='organization', cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', back_populates='organization', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'industry': self.industry,
            'size': self.size,
            'plan': self.plan.to_dict() if self.plan else None,
            'subscription_status': self.subscription_status,
            'trial_start_date': self.trial_start_date.isoformat() if self.trial_start_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'subscription_start_date': self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'employee_limit': self.employee_limit,
            'current_employee_count': self.current_employee_count,
            'storage_limit_gb': self.storage_limit_gb,
            'current_storage_gb': self.current_storage_gb,
            'billing_email': self.billing_email,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'timezone': self.timezone,
            'date_format': self.date_format,
            'currency': self.currency,
            'enable_two_factor': self.enable_two_factor,
            'session_timeout_minutes': self.session_timeout_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_within_limits(self):
        """Check if organization is within usage limits"""
        return {
            'employees': self.current_employee_count < self.employee_limit,
            'storage': self.current_storage_gb < self.storage_limit_gb,
            'subscription_active': self.subscription_status == 'active' or self.is_trial_active()
        }
    
    def is_trial_active(self):
        """Check if trial period is still active"""
        if self.subscription_status == 'trial' and self.trial_end_date:
            return date.today() <= self.trial_end_date
        return False
    
    def days_until_trial_expires(self):
        """Calculate days remaining in trial"""
        if self.is_trial_active():
            return (self.trial_end_date - date.today()).days
        return 0


class SubscriptionPlan(db.Model):
    """SaaS subscription plans"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Free, Starter, Professional, Enterprise
    slug = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    price_monthly = db.Column(db.Float, default=0.0)
    price_yearly = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Limits and features
    employee_limit = db.Column(db.Integer, default=5)
    storage_limit_gb = db.Column(db.Integer, default=1)
    api_calls_per_month = db.Column(db.Integer, default=1000)
    
    # Feature flags
    features = db.Column(db.JSON)  # Store feature availability as JSON
    
    # Plan metadata
    is_active = db.Column(db.Boolean, default=True)
    is_popular = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    trial_days = db.Column(db.Integer, default=14)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organizations = db.relationship('Organization', back_populates='plan')
    subscriptions = db.relationship('Subscription', back_populates='plan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price_monthly': self.price_monthly,
            'price_yearly': self.price_yearly,
            'currency': self.currency,
            'employee_limit': self.employee_limit,
            'storage_limit_gb': self.storage_limit_gb,
            'api_calls_per_month': self.api_calls_per_month,
            'features': self.features,
            'is_active': self.is_active,
            'is_popular': self.is_popular,
            'trial_days': self.trial_days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Subscription(db.Model):
    """Track subscription history and billing"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Billing details
    billing_cycle = db.Column(db.String(10), default='monthly')  # monthly, yearly
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Payment information
    stripe_subscription_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))  # card, paypal, bank_transfer
    
    # Subscription period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    next_billing_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, past_due
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='subscriptions')
    plan = db.relationship('SubscriptionPlan', back_populates='subscriptions')
    invoices = db.relationship('Invoice', back_populates='subscription', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'billing_cycle': self.billing_cycle,
            'amount': self.amount,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'status': self.status,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Invoice(db.Model):
    """Track billing and invoices"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Amount details
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Billing period
    billing_period_start = db.Column(db.Date, nullable=False)
    billing_period_end = db.Column(db.Date, nullable=False)
    
    # Payment status
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    paid_at = db.Column(db.DateTime)
    due_date = db.Column(db.Date, nullable=False)
    
    # Payment details
    stripe_invoice_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = db.relationship('Subscription', back_populates='invoices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'invoice_number': self.invoice_number,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'billing_period_start': self.billing_period_start.isoformat() if self.billing_period_start else None,
            'billing_period_end': self.billing_period_end.isoformat() if self.billing_period_end else None,
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UsageLog(db.Model):
    """Track usage for billing and analytics"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Usage metrics
    metric_type = db.Column(db.String(50), nullable=False)  # api_calls, storage, employees, etc.
    metric_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))  # calls, gb, count, etc.
    
    # Time tracking
    recorded_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='usage_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'unit': self.unit,
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }