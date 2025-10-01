from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import date, datetime, timedelta
from app import db
from app.models.organization import Organization, SubscriptionPlan, Subscription, Invoice, UsageLog
from app.models.employee import Employee
import secrets
import string
import re

bp = Blueprint('organizations', __name__, url_prefix='/api/organizations')

def generate_slug(name):
    """Generate a URL-safe slug from organization name"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    
    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while Organization.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

@bp.route('/register', methods=['POST'])
def register_organization():
    """Register a new organization for SaaS"""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'admin_first_name', 'admin_last_name', 'admin_email', 'admin_password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email already exists
    if Organization.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Organization email already exists'}), 400
    
    # Check if admin email already exists across all organizations
    if Employee.query.filter_by(email=data['admin_email']).first():
        return jsonify({'error': 'Admin email already exists'}), 400
    
    try:
        # Get the default starter plan
        starter_plan = SubscriptionPlan.query.filter_by(slug='starter').first()
        if not starter_plan:
            # Create default plans if they don't exist
            create_default_plans()
            starter_plan = SubscriptionPlan.query.filter_by(slug='starter').first()
        
        # Create organization
        organization = Organization(
            name=data['name'],
            slug=generate_slug(data['name']),
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            website=data.get('website'),
            industry=data.get('industry'),
            size=data.get('size'),
            plan_id=starter_plan.id,
            subscription_status='trial',
            trial_start_date=date.today(),
            trial_end_date=date.today() + timedelta(days=starter_plan.trial_days),
            employee_limit=starter_plan.employee_limit,
            storage_limit_gb=starter_plan.storage_limit_gb,
            billing_email=data.get('billing_email', data['email'])
        )
        
        db.session.add(organization)
        db.session.flush()  # Get the organization ID
        
        # Create admin user
        admin_employee = Employee(
            organization_id=organization.id,
            employee_id='ADMIN001',
            email=data['admin_email'],
            first_name=data['admin_first_name'],
            last_name=data['admin_last_name'],
            position='Administrator',
            hire_date=date.today(),
            role='admin',
            status='active'
        )
        admin_employee.set_password(data['admin_password'])
        
        db.session.add(admin_employee)
        
        # Update organization employee count
        organization.current_employee_count = 1
        
        db.session.commit()
        
        # Create access token for immediate login
        access_token = create_access_token(identity=admin_employee.id)
        
        return jsonify({
            'message': 'Organization registered successfully',
            'organization': organization.to_dict(),
            'admin_user': admin_employee.to_dict(),
            'access_token': access_token,
            'trial_expires_in_days': organization.days_until_trial_expires()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization(org_id):
    """Get organization details"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.organization_id != org_id:
        return jsonify({'error': 'Access denied'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    
    # Add additional statistics
    org_data = organization.to_dict()
    org_data['limits_status'] = organization.is_within_limits()
    org_data['trial_expires_in_days'] = organization.days_until_trial_expires()
    
    return jsonify(org_data), 200

@bp.route('/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_organization(org_id):
    """Update organization settings"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.organization_id != org_id or employee.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    # Update basic information
    if 'name' in data:
        organization.name = data['name']
    if 'email' in data:
        organization.email = data['email']
    if 'phone' in data:
        organization.phone = data['phone']
    if 'address' in data:
        organization.address = data['address']
    if 'website' in data:
        organization.website = data['website']
    if 'industry' in data:
        organization.industry = data['industry']
    if 'size' in data:
        organization.size = data['size']
    
    # Update settings
    if 'primary_color' in data:
        organization.primary_color = data['primary_color']
    if 'timezone' in data:
        organization.timezone = data['timezone']
    if 'date_format' in data:
        organization.date_format = data['date_format']
    if 'currency' in data:
        organization.currency = data['currency']
    if 'enable_two_factor' in data:
        organization.enable_two_factor = data['enable_two_factor']
    if 'session_timeout_minutes' in data:
        organization.session_timeout_minutes = data['session_timeout_minutes']
    
    organization.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(organization.to_dict()), 200

@bp.route('/<int:org_id>/usage', methods=['GET'])
@jwt_required()
def get_organization_usage(org_id):
    """Get organization usage statistics"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.organization_id != org_id:
        return jsonify({'error': 'Access denied'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    
    # Get usage logs for the current month
    current_month = date.today().replace(day=1)
    usage_logs = UsageLog.query.filter(
        UsageLog.organization_id == org_id,
        UsageLog.recorded_date >= current_month
    ).all()
    
    # Aggregate usage by metric type
    usage_summary = {}
    for log in usage_logs:
        if log.metric_type not in usage_summary:
            usage_summary[log.metric_type] = {
                'total': 0,
                'unit': log.unit,
                'logs': []
            }
        usage_summary[log.metric_type]['total'] += log.metric_value
        usage_summary[log.metric_type]['logs'].append(log.to_dict())
    
    return jsonify({
        'organization_id': org_id,
        'current_limits': {
            'employees': f"{organization.current_employee_count}/{organization.employee_limit}",
            'storage_gb': f"{organization.current_storage_gb:.2f}/{organization.storage_limit_gb}"
        },
        'usage_summary': usage_summary,
        'limits_status': organization.is_within_limits()
    }), 200

@bp.route('/<int:org_id>/subscription', methods=['GET'])
@jwt_required()
def get_subscription_info(org_id):
    """Get current subscription information"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.organization_id != org_id:
        return jsonify({'error': 'Access denied'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    current_subscription = Subscription.query.filter_by(
        organization_id=org_id,
        status='active'
    ).first()
    
    # Get recent invoices
    recent_invoices = []
    if current_subscription:
        recent_invoices = Invoice.query.filter_by(
            subscription_id=current_subscription.id
        ).order_by(Invoice.created_at.desc()).limit(5).all()
    
    return jsonify({
        'organization': organization.to_dict(),
        'current_subscription': current_subscription.to_dict() if current_subscription else None,
        'recent_invoices': [invoice.to_dict() for invoice in recent_invoices],
        'trial_expires_in_days': organization.days_until_trial_expires()
    }), 200

def create_default_plans():
    """Create default subscription plans"""
    plans = [
        {
            'name': 'Free',
            'slug': 'free',
            'description': 'Perfect for small teams getting started',
            'price_monthly': 0.0,
            'price_yearly': 0.0,
            'employee_limit': 5,
            'storage_limit_gb': 1,
            'api_calls_per_month': 1000,
            'trial_days': 0,
            'features': {
                'employee_management': True,
                'attendance_tracking': True,
                'basic_reports': True,
                'email_support': True,
                'api_access': False,
                'custom_branding': False,
                'advanced_reports': False,
                'integrations': False,
                'priority_support': False
            }
        },
        {
            'name': 'Starter',
            'slug': 'starter',
            'description': 'Ideal for growing teams',
            'price_monthly': 29.0,
            'price_yearly': 290.0,
            'employee_limit': 25,
            'storage_limit_gb': 5,
            'api_calls_per_month': 5000,
            'trial_days': 14,
            'features': {
                'employee_management': True,
                'attendance_tracking': True,
                'basic_reports': True,
                'email_support': True,
                'api_access': True,
                'custom_branding': False,
                'advanced_reports': True,
                'integrations': False,
                'priority_support': False
            }
        },
        {
            'name': 'Professional',
            'slug': 'professional',
            'description': 'Complete solution for medium businesses',
            'price_monthly': 99.0,
            'price_yearly': 990.0,
            'employee_limit': 100,
            'storage_limit_gb': 25,
            'api_calls_per_month': 25000,
            'trial_days': 14,
            'is_popular': True,
            'features': {
                'employee_management': True,
                'attendance_tracking': True,
                'basic_reports': True,
                'email_support': True,
                'api_access': True,
                'custom_branding': True,
                'advanced_reports': True,
                'integrations': True,
                'priority_support': True
            }
        },
        {
            'name': 'Enterprise',
            'slug': 'enterprise',
            'description': 'Advanced features for large organizations',
            'price_monthly': 299.0,
            'price_yearly': 2990.0,
            'employee_limit': 1000,
            'storage_limit_gb': 100,
            'api_calls_per_month': 100000,
            'trial_days': 30,
            'features': {
                'employee_management': True,
                'attendance_tracking': True,
                'basic_reports': True,
                'email_support': True,
                'api_access': True,
                'custom_branding': True,
                'advanced_reports': True,
                'integrations': True,
                'priority_support': True,
                'dedicated_support': True,
                'sso': True,
                'advanced_security': True,
                'custom_fields': True
            }
        }
    ]
    
    for plan_data in plans:
        existing_plan = SubscriptionPlan.query.filter_by(slug=plan_data['slug']).first()
        if not existing_plan:
            plan = SubscriptionPlan(**plan_data)
            db.session.add(plan)
    
    db.session.commit()

@bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans (public endpoint)"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.sort_order).all()
    return jsonify([plan.to_dict() for plan in plans]), 200

@bp.route('/<int:org_id>/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription(org_id):
    """Upgrade organization subscription"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.organization_id != org_id or employee.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    plan_id = data.get('plan_id')
    billing_cycle = data.get('billing_cycle', 'monthly')
    
    if not plan_id:
        return jsonify({'error': 'plan_id is required'}), 400
    
    organization = Organization.query.get_or_404(org_id)
    new_plan = SubscriptionPlan.query.get_or_404(plan_id)
    
    # Update organization plan and limits
    organization.plan_id = plan_id
    organization.employee_limit = new_plan.employee_limit
    organization.storage_limit_gb = new_plan.storage_limit_gb
    organization.subscription_status = 'active'
    organization.subscription_start_date = date.today()
    organization.subscription_end_date = date.today() + timedelta(days=30 if billing_cycle == 'monthly' else 365)
    
    # Create subscription record
    amount = new_plan.price_monthly if billing_cycle == 'monthly' else new_plan.price_yearly
    subscription = Subscription(
        organization_id=org_id,
        plan_id=plan_id,
        billing_cycle=billing_cycle,
        amount=amount,
        start_date=date.today(),
        end_date=organization.subscription_end_date,
        next_billing_date=date.today() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
        status='active'
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription upgraded successfully',
        'organization': organization.to_dict(),
        'subscription': subscription.to_dict()
    }), 200