from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.organization import Organization, SubscriptionPlan, Subscription, Invoice, UsageLog
from app.models.employee import Employee

bp = Blueprint('saas_admin', __name__, url_prefix='/api/saas-admin')

def is_super_admin():
    """Check if current user is a super admin"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    # Super admin check - you can modify this logic
    # For now, checking if email contains 'superadmin' or is from specific domain
    if employee and (
        'superadmin' in employee.email.lower() or 
        employee.email.endswith('@saas-admin.com') or
        employee.role == 'super_admin'
    ):
        return True
    return False

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_saas_dashboard():
    """Get SaaS admin dashboard statistics"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    # Get basic statistics
    total_organizations = Organization.query.count()
    active_organizations = Organization.query.filter_by(is_active=True).count()
    trial_organizations = Organization.query.filter_by(subscription_status='trial').count()
    paid_organizations = Organization.query.filter_by(subscription_status='active').count()
    
    # Get subscription statistics by plan
    plan_stats = db.session.query(
        SubscriptionPlan.name,
        func.count(Organization.id).label('count')
    ).join(Organization, Organization.plan_id == SubscriptionPlan.id).group_by(
        SubscriptionPlan.name
    ).all()
    
    # Get revenue statistics (last 12 months)
    twelve_months_ago = date.today() - timedelta(days=365)
    monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Invoice.created_at).label('month'),
        func.sum(Invoice.total_amount).label('revenue')
    ).filter(
        Invoice.created_at >= twelve_months_ago,
        Invoice.status == 'paid'
    ).group_by(
        func.strftime('%Y-%m', Invoice.created_at)
    ).order_by('month').all()
    
    # Get recent activities
    recent_organizations = Organization.query.order_by(
        Organization.created_at.desc()
    ).limit(10).all()
    
    # Calculate churn rate (simplified)
    last_month = date.today().replace(day=1) - timedelta(days=1)
    last_month_start = last_month.replace(day=1)
    
    cancelled_last_month = Subscription.query.filter(
        Subscription.cancelled_at >= last_month_start,
        Subscription.cancelled_at <= last_month
    ).count()
    
    active_start_month = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.start_date <= last_month_start
    ).count()
    
    churn_rate = (cancelled_last_month / active_start_month * 100) if active_start_month > 0 else 0
    
    return jsonify({
        'overview': {
            'total_organizations': total_organizations,
            'active_organizations': active_organizations,
            'trial_organizations': trial_organizations,
            'paid_organizations': paid_organizations,
            'churn_rate': round(churn_rate, 2)
        },
        'plan_distribution': [{'plan': stat[0], 'count': stat[1]} for stat in plan_stats],
        'monthly_revenue': [{'month': stat[0], 'revenue': float(stat[1])} for stat in monthly_revenue],
        'recent_organizations': [org.to_dict() for org in recent_organizations]
    }), 200

@bp.route('/organizations', methods=['GET'])
@jwt_required()
def get_all_organizations():
    """Get all organizations with filtering"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')  # trial, active, suspended, cancelled
    plan_id = request.args.get('plan_id', type=int)
    search = request.args.get('search')
    
    query = Organization.query
    
    if status:
        query = query.filter_by(subscription_status=status)
    if plan_id:
        query = query.filter_by(plan_id=plan_id)
    if search:
        query = query.filter(
            db.or_(
                Organization.name.ilike(f'%{search}%'),
                Organization.email.ilike(f'%{search}%'),
                Organization.slug.ilike(f'%{search}%')
            )
        )
    
    organizations = query.order_by(Organization.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'organizations': [org.to_dict() for org in organizations.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': organizations.total,
            'pages': organizations.pages,
            'has_next': organizations.has_next,
            'has_prev': organizations.has_prev
        }
    }), 200

@bp.route('/organizations/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization_details(org_id):
    """Get detailed organization information"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    
    # Get employees count
    employees_count = Employee.query.filter_by(organization_id=org_id).count()
    
    # Get subscription history
    subscriptions = Subscription.query.filter_by(
        organization_id=org_id
    ).order_by(Subscription.created_at.desc()).all()
    
    # Get recent usage
    recent_usage = UsageLog.query.filter_by(
        organization_id=org_id
    ).order_by(UsageLog.created_at.desc()).limit(20).all()
    
    # Get invoices
    invoice_query = db.session.query(Invoice).join(Subscription).filter(
        Subscription.organization_id == org_id
    ).order_by(Invoice.created_at.desc()).limit(10)
    invoices = invoice_query.all()
    
    return jsonify({
        'organization': organization.to_dict(),
        'employees_count': employees_count,
        'subscriptions': [sub.to_dict() for sub in subscriptions],
        'recent_usage': [usage.to_dict() for usage in recent_usage],
        'recent_invoices': [invoice.to_dict() for invoice in invoices],
        'limits_status': organization.is_within_limits()
    }), 200

@bp.route('/organizations/<int:org_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_organization(org_id):
    """Suspend an organization"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    reason = data.get('reason', 'Administrative action')
    
    organization.subscription_status = 'suspended'
    organization.is_active = False
    organization.updated_at = datetime.utcnow()
    
    # Cancel active subscription
    active_subscription = Subscription.query.filter_by(
        organization_id=org_id,
        status='active'
    ).first()
    
    if active_subscription:
        active_subscription.status = 'cancelled'
        active_subscription.cancelled_at = datetime.utcnow()
        active_subscription.cancellation_reason = f"Admin suspension: {reason}"
    
    db.session.commit()
    
    return jsonify({
        'message': 'Organization suspended successfully',
        'organization': organization.to_dict()
    }), 200

@bp.route('/organizations/<int:org_id>/activate', methods=['POST'])
@jwt_required()
def activate_organization(org_id):
    """Reactivate a suspended organization"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    organization = Organization.query.get_or_404(org_id)
    
    organization.subscription_status = 'active'
    organization.is_active = True
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Organization activated successfully',
        'organization': organization.to_dict()
    }), 200

@bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans_admin():
    """Get all subscription plans for admin"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    plans = SubscriptionPlan.query.order_by(SubscriptionPlan.sort_order).all()
    
    # Add usage statistics for each plan
    plan_data = []
    for plan in plans:
        plan_dict = plan.to_dict()
        plan_dict['organization_count'] = Organization.query.filter_by(plan_id=plan.id).count()
        plan_data.append(plan_dict)
    
    return jsonify(plan_data), 200

@bp.route('/plans', methods=['POST'])
@jwt_required()
def create_plan():
    """Create a new subscription plan"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    data = request.get_json()
    required_fields = ['name', 'slug', 'price_monthly', 'employee_limit', 'storage_limit_gb']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if slug is unique
    if SubscriptionPlan.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Plan slug already exists'}), 400
    
    plan = SubscriptionPlan(
        name=data['name'],
        slug=data['slug'],
        description=data.get('description'),
        price_monthly=data['price_monthly'],
        price_yearly=data.get('price_yearly', data['price_monthly'] * 10),  # 10x monthly for yearly
        employee_limit=data['employee_limit'],
        storage_limit_gb=data['storage_limit_gb'],
        api_calls_per_month=data.get('api_calls_per_month', 1000),
        features=data.get('features', {}),
        trial_days=data.get('trial_days', 14),
        is_active=data.get('is_active', True),
        is_popular=data.get('is_popular', False),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify(plan.to_dict()), 201

@bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    """Update a subscription plan"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    # Update plan fields
    if 'name' in data:
        plan.name = data['name']
    if 'description' in data:
        plan.description = data['description']
    if 'price_monthly' in data:
        plan.price_monthly = data['price_monthly']
    if 'price_yearly' in data:
        plan.price_yearly = data['price_yearly']
    if 'employee_limit' in data:
        plan.employee_limit = data['employee_limit']
    if 'storage_limit_gb' in data:
        plan.storage_limit_gb = data['storage_limit_gb']
    if 'api_calls_per_month' in data:
        plan.api_calls_per_month = data['api_calls_per_month']
    if 'features' in data:
        plan.features = data['features']
    if 'trial_days' in data:
        plan.trial_days = data['trial_days']
    if 'is_active' in data:
        plan.is_active = data['is_active']
    if 'is_popular' in data:
        plan.is_popular = data['is_popular']
    if 'sort_order' in data:
        plan.sort_order = data['sort_order']
    
    plan.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(plan.to_dict()), 200

@bp.route('/analytics/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analytics():
    """Get detailed revenue analytics"""
    if not is_super_admin():
        return jsonify({'error': 'Super admin access required'}), 403
    
    # Get time range from query params
    days = request.args.get('days', 30, type=int)
    start_date = date.today() - timedelta(days=days)
    
    # Daily revenue
    daily_revenue = db.session.query(
        func.date(Invoice.paid_at).label('date'),
        func.sum(Invoice.total_amount).label('revenue'),
        func.count(Invoice.id).label('invoice_count')
    ).filter(
        Invoice.paid_at >= start_date,
        Invoice.status == 'paid'
    ).group_by(
        func.date(Invoice.paid_at)
    ).order_by('date').all()
    
    # Revenue by plan
    plan_revenue = db.session.query(
        SubscriptionPlan.name,
        func.sum(Invoice.total_amount).label('revenue'),
        func.count(Invoice.id).label('invoice_count')
    ).join(Subscription).join(Invoice).filter(
        Invoice.paid_at >= start_date,
        Invoice.status == 'paid'
    ).group_by(SubscriptionPlan.name).all()
    
    # Calculate totals
    total_revenue = sum(day[1] for day in daily_revenue) if daily_revenue else 0
    total_invoices = sum(day[2] for day in daily_revenue) if daily_revenue else 0
    avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
    
    return jsonify({
        'summary': {
            'total_revenue': float(total_revenue),
            'total_invoices': total_invoices,
            'avg_invoice_value': float(avg_invoice_value),
            'period_days': days
        },
        'daily_revenue': [
            {
                'date': day[0].isoformat(),
                'revenue': float(day[1]),
                'invoice_count': day[2]
            } for day in daily_revenue
        ],
        'revenue_by_plan': [
            {
                'plan': plan[0],
                'revenue': float(plan[1]),
                'invoice_count': plan[2]
            } for plan in plan_revenue
        ]
    }), 200