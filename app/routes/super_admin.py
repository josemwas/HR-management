from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from app.models.organization import Organization, SubscriptionPlan
from datetime import datetime, timedelta

bp = Blueprint('super_admin', __name__, url_prefix='/api/super-admin')

def require_super_admin():
    """Decorator to require super admin role"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_employee_id = get_jwt_identity()
            current_employee = Employee.query.get(current_employee_id)
            
            if not current_employee or current_employee.role != 'super_admin':
                return jsonify({'error': 'Super admin access required'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@bp.route('/organizations', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_organizations():
    """Get all organizations for super admin management"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Organization.query
    
    if search:
        query = query.filter(
            Organization.name.contains(search) |
            Organization.email.contains(search) |
            Organization.industry.contains(search)
        )
    
    organizations = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = []
    for org in organizations.items:
        org_data = org.to_dict()
        org_data['feature_settings'] = org.feature_settings if hasattr(org, 'feature_settings') else {}
        org_data['employee_count'] = len(org.employees)
        org_data['admin_user'] = next((emp.to_dict() for emp in org.employees if emp.role == 'admin'), None)
        result.append(org_data)
    
    return jsonify({
        'organizations': result,
        'pagination': {
            'page': page,
            'pages': organizations.pages,
            'per_page': per_page,
            'total': organizations.total,
            'has_next': organizations.has_next,
            'has_prev': organizations.has_prev
        }
    }), 200

@bp.route('/organizations/<int:org_id>/features', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_organization_features(org_id):
    """Get feature settings for an organization"""
    organization = Organization.query.get_or_404(org_id)
    
    # Default feature settings
    default_features = {
        'employee_management': True,
        'department_management': True,
        'attendance_tracking': True,
        'leave_management': True,
        'payroll_management': True,
        'performance_reviews': True,
        'recruitment_tools': True,
        'analytics_reporting': True,
        'api_access': True,
        'mobile_app_access': True,
        'integrations': True,
        'custom_fields': True,
        'audit_logs': True,
        'advanced_security': True,
        'backup_restore': True,
        'bulk_operations': True,
        'document_management': True,
        'notification_system': True,
        'calendar_integration': True,
        'time_tracking': True
    }
    
    # Get current feature settings (stored in JSON field)
    current_features = organization.feature_settings if hasattr(organization, 'feature_settings') and organization.feature_settings else default_features
    
    # Merge with defaults to ensure all features are present
    for feature, default_value in default_features.items():
        if feature not in current_features:
            current_features[feature] = default_value
    
    return jsonify({
        'organization': organization.to_dict(),
        'features': current_features,
        'plan_features': organization.plan.features if organization.plan else []
    }), 200

@bp.route('/organizations/<int:org_id>', methods=['PUT'])
@jwt_required()
@require_super_admin()
def update_organization(org_id):
    """Update organization basic information"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update allowed fields
    allowed_fields = [
        'name', 'email', 'phone', 'website', 'address', 'industry', 
        'size', 'timezone', 'currency', 'date_format', 'primary_color',
        'employee_limit', 'storage_limit_gb', 'session_timeout_minutes',
        'enable_two_factor', 'billing_email'
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(organization, field, data[field])
    
    organization.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Organization updated successfully',
            'organization': organization.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/organizations/<int:org_id>/features', methods=['POST'])
@jwt_required()
@require_super_admin()
def toggle_organization_feature(org_id):
    """Toggle a specific feature for an organization"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    if not data or 'feature' not in data or 'enabled' not in data:
        return jsonify({'error': 'Feature name and enabled status are required'}), 400
    
    feature_name = data['feature']
    enabled = data['enabled']
    
    # Get current feature settings or initialize with defaults
    current_features = organization.feature_settings if hasattr(organization, 'feature_settings') and organization.feature_settings else {}
    
    # Update the specific feature
    current_features[feature_name] = enabled
    
    # Store updated settings
    organization.feature_settings = current_features
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Feature {feature_name} {"enabled" if enabled else "disabled"} successfully',
        'organization': organization.to_dict(),
        'feature': feature_name,
        'enabled': enabled
    }), 200

@bp.route('/organizations/<int:org_id>/features', methods=['PUT'])
@jwt_required()
@require_super_admin()
def update_organization_features(org_id):
    """Update feature settings for an organization"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    if not data or 'features' not in data:
        return jsonify({'error': 'Features data is required'}), 400
    
    # Store feature settings
    organization.feature_settings = data['features']
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Organization features updated successfully',
        'organization': organization.to_dict(),
        'features': organization.feature_settings
    }), 200

@bp.route('/organizations/<int:org_id>/suspend', methods=['POST'])
@jwt_required()
@require_super_admin()
def suspend_organization(org_id):
    """Suspend an organization"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    reason = data.get('reason', 'Administrative action') if data else 'Administrative action'
    
    organization.is_active = False
    organization.suspension_reason = reason
    organization.suspended_at = datetime.utcnow()
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Organization {organization.name} has been suspended',
        'organization': organization.to_dict()
    }), 200

@bp.route('/organizations/<int:org_id>/activate', methods=['POST'])
@jwt_required()
@require_super_admin()
def activate_organization(org_id):
    """Activate a suspended organization"""
    organization = Organization.query.get_or_404(org_id)
    
    organization.is_active = True
    organization.suspension_reason = None
    organization.suspended_at = None
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Organization {organization.name} has been activated',
        'organization': organization.to_dict()
    }), 200

@bp.route('/plans', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_subscription_plans():
    """Get all available subscription plans"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    
    return jsonify({
        'plans': [plan.to_dict() for plan in plans]
    }), 200

@bp.route('/organizations/<int:org_id>/change-plan', methods=['POST'])
@jwt_required()
@require_super_admin()
def change_organization_plan(org_id):
    """Change an organization's subscription plan"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    if not data or not data.get('plan_id'):
        return jsonify({'error': 'Plan ID is required'}), 400
    
    plan = SubscriptionPlan.query.get_or_404(data['plan_id'])
    
    # Update organization plan
    organization.plan_id = plan.id
    organization.employee_limit = plan.employee_limit
    organization.storage_limit_gb = plan.storage_limit_gb
    organization.updated_at = datetime.utcnow()
    
    # If changing to a paid plan, update subscription status
    if plan.price_monthly > 0 and organization.subscription_status == 'trial':
        organization.subscription_status = 'active'
        organization.subscription_start_date = datetime.utcnow().date()
        organization.subscription_end_date = datetime.utcnow().date() + timedelta(days=30)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Organization plan changed to {plan.name}',
        'organization': organization.to_dict(),
        'new_plan': plan.to_dict()
    }), 200

@bp.route('/organizations/<int:org_id>/extend-trial', methods=['POST'])
@jwt_required()
@require_super_admin()
def extend_trial(org_id):
    """Extend trial period for an organization"""
    organization = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    days = data.get('days', 30) if data else 30
    
    if organization.subscription_status != 'trial':
        return jsonify({'error': 'Organization is not in trial period'}), 400
    
    # Extend trial
    current_end = organization.trial_end_date or datetime.utcnow().date()
    organization.trial_end_date = current_end + timedelta(days=days)
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Trial extended by {days} days',
        'organization': organization.to_dict(),
        'new_trial_end_date': organization.trial_end_date.isoformat()
    }), 200

@bp.route('/organizations/<int:org_id>/usage-stats', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_organization_usage(org_id):
    """Get usage statistics for an organization"""
    organization = Organization.query.get_or_404(org_id)
    
    # Calculate usage statistics
    employee_count = len(organization.employees)
    department_count = len(organization.departments)
    
    # Get recent activity (last 30 days)
    from datetime import date
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    
    recent_logins = Employee.query.filter_by(organization_id=org_id).filter(
        Employee.updated_at >= thirty_days_ago
    ).count()
    
    usage_stats = {
        'employee_count': employee_count,
        'employee_limit': organization.employee_limit,
        'employee_usage_percent': (employee_count / organization.employee_limit * 100) if organization.employee_limit > 0 else 0,
        'department_count': department_count,
        'storage_used_gb': organization.current_storage_gb,
        'storage_limit_gb': organization.storage_limit_gb,
        'storage_usage_percent': (organization.current_storage_gb / organization.storage_limit_gb * 100) if organization.storage_limit_gb > 0 else 0,
        'recent_logins_30_days': recent_logins,
        'subscription_status': organization.subscription_status,
        'trial_days_remaining': organization.days_until_trial_expires() if organization.subscription_status == 'trial' else 0
    }
    
    return jsonify({
        'organization': organization.to_dict(),
        'usage_stats': usage_stats
    }), 200

@bp.route('/stats', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_super_admin_stats():
    """Get super admin dashboard statistics"""
    total_organizations = Organization.query.count()
    active_organizations = Organization.query.filter_by(is_active=True).count()
    trial_organizations = Organization.query.filter_by(subscription_status='trial').count()
    paid_organizations = Organization.query.filter_by(subscription_status='active').count()
    
    total_employees = Employee.query.count()
    
    # Calculate monthly revenue (mock data for now)
    monthly_revenue = 50000  # This should come from actual billing data
    
    return jsonify({
        'total_organizations': total_organizations,
        'active_organizations': active_organizations,
        'total_employees': total_employees,
        'monthly_revenue': monthly_revenue
    }), 200

@bp.route('/system-info', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_system_info():
    """Get system information for super admin"""
    import psutil
    import os
    from datetime import datetime
    
    # Calculate database size (approximation)
    db_size = "15.2 MB"  # This should be calculated from actual database
    
    # Get system metrics
    memory = psutil.virtual_memory()
    memory_usage = f"{memory.percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)"
    
    # Mock data for other metrics
    api_calls_today = 2847
    active_sessions = 142
    
    return jsonify({
        'db_size': db_size,
        'organization_count': Organization.query.count(),
        'employee_count': Employee.query.count(),
        'last_backup': 'October 1, 2025 23:00',
        'uptime': '5 days, 12 hours',
        'memory_usage': memory_usage,
        'api_calls_today': api_calls_today,
        'active_sessions': active_sessions
    }), 200

@bp.route('/organizations/<int:org_id>/features/enable-all', methods=['POST'])
@jwt_required()
@require_super_admin()
def enable_all_features(org_id):
    """Enable all features for an organization"""
    organization = Organization.query.get_or_404(org_id)
    
    # All features enabled
    all_features = {
        'employee_management': True,
        'department_management': True,
        'attendance_tracking': True,
        'leave_management': True,
        'payroll_management': True,
        'performance_reviews': True,
        'recruitment_tools': True,
        'analytics_reporting': True,
        'api_access': True,
        'mobile_app_access': True,
        'integrations': True,
        'custom_fields': True,
        'audit_logs': True,
        'advanced_security': True,
        'backup_restore': True,
        'bulk_operations': True,
        'document_management': True,
        'notification_system': True,
        'calendar_integration': True,
        'time_tracking': True
    }
    
    organization.feature_settings = all_features
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'All features enabled successfully',
        'organization': organization.to_dict(),
        'features': all_features
    }), 200

@bp.route('/organizations/<int:org_id>/features/disable-all', methods=['POST'])
@jwt_required()
@require_super_admin()
def disable_all_features(org_id):
    """Disable all features for an organization"""
    organization = Organization.query.get_or_404(org_id)
    
    # All features disabled (keep basic employee management)
    minimal_features = {
        'employee_management': True,  # Keep this as it's core functionality
        'department_management': False,
        'attendance_tracking': False,
        'leave_management': False,
        'payroll_management': False,
        'performance_reviews': False,
        'recruitment_tools': False,
        'analytics_reporting': False,
        'api_access': False,
        'mobile_app_access': False,
        'integrations': False,
        'custom_fields': False,
        'audit_logs': False,
        'advanced_security': False,
        'backup_restore': False,
        'bulk_operations': False,
        'document_management': False,
        'notification_system': False,
        'calendar_integration': False,
        'time_tracking': False
    }
    
    organization.feature_settings = minimal_features
    organization.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'All features disabled successfully (except basic employee management)',
        'organization': organization.to_dict(),
        'features': minimal_features
    }), 200

@bp.route('/platform-stats', methods=['GET'])
@jwt_required()
@require_super_admin()
def get_platform_stats():
    """Get platform-wide statistics"""
    total_organizations = Organization.query.count()
    active_organizations = Organization.query.filter_by(is_active=True).count()
    trial_organizations = Organization.query.filter_by(subscription_status='trial').count()
    paid_organizations = Organization.query.filter_by(subscription_status='active').count()
    
    total_employees = Employee.query.count()
    
    # Get plan distribution
    plan_stats = db.session.query(
        SubscriptionPlan.name,
        db.func.count(Organization.id)
    ).join(Organization).group_by(SubscriptionPlan.id, SubscriptionPlan.name).all()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = Organization.query.filter(
        Organization.created_at >= thirty_days_ago
    ).count()
    
    stats = {
        'total_organizations': total_organizations,
        'active_organizations': active_organizations,
        'suspended_organizations': total_organizations - active_organizations,
        'trial_organizations': trial_organizations,
        'paid_organizations': paid_organizations,
        'total_employees': total_employees,
        'recent_registrations_30_days': recent_registrations,
        'plan_distribution': [{'plan': name, 'count': count} for name, count in plan_stats]
    }
    
    return jsonify({'platform_stats': stats}), 200