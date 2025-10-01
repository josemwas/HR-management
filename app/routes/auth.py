from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from app.models.organization import Organization, SubscriptionPlan
from datetime import datetime, timedelta
import secrets
import string
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """Authenticate employee and return JWT tokens"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    # Support both organization-scoped and global login
    organization_slug = data.get('organization_slug')
    
    if organization_slug:
        # Organization-specific login
        organization = Organization.query.filter_by(slug=organization_slug).first()
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
            
        if not organization.is_active:
            return jsonify({'error': 'Organization is suspended'}), 403
            
        employee = Employee.query.filter_by(
            email=email,
            organization_id=organization.id
        ).first()
    else:
        # Global login (find employee across all organizations)
        employee = Employee.query.filter_by(email=email).first()
        
        if employee and employee.organization:
            organization = employee.organization
            if not organization.is_active:
                return jsonify({'error': 'Organization is suspended'}), 403
    
    if not employee:
        return jsonify({'error': 'Invalid email or password'}), 401
        
    if not employee.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if employee.status not in ['active']:
        return jsonify({'error': 'Account is not active'}), 403
    
    # Check organization limits and subscription status
    if employee.organization:
        limits_status = employee.organization.is_within_limits()
        if not limits_status['subscription_active']:
            return jsonify({'error': 'Organization subscription is inactive'}), 403
    
    access_token = create_access_token(identity=str(employee.id))
    refresh_token = create_refresh_token(identity=str(employee.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'employee': employee.to_dict(),
        'organization': employee.organization.to_dict() if employee.organization else None
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=str(identity))
    return jsonify({'access_token': access_token}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_employee():
    """Get current authenticated employee"""
    employee_id = get_jwt_identity()
    employee = Employee.query.get_or_404(int(employee_id))
    
    response_data = {
        'employee': employee.to_dict(),
        'organization': employee.organization.to_dict() if employee.organization else None
    }
    
    # Add organization limits and trial info for admins
    if employee.role in ['admin', 'super_admin'] and employee.organization:
        response_data['organization_limits'] = employee.organization.is_within_limits()
        response_data['trial_expires_in_days'] = employee.organization.days_until_trial_expires()
    
    return jsonify(response_data), 200

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change employee password"""
    data = request.get_json()
    employee_id = get_jwt_identity()
    employee = Employee.query.get_or_404(int(employee_id))
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old and new passwords are required'}), 400
    
    if not employee.check_password(data['old_password']):
        return jsonify({'error': 'Invalid old password'}), 401
    
    # Validate new password
    if len(data['new_password']) < 8:
        return jsonify({'error': 'New password must be at least 8 characters long'}), 400
    
    employee.set_password(data['new_password'])
    employee.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@bp.route('/register-organization', methods=['POST'])
def register_organization():
    """Register a new organization and create admin user"""
    data = request.get_json()
    
    required_fields = ['organization_name', 'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['admin_email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if email already exists
    if Employee.query.filter_by(email=data['admin_email'].strip().lower()).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Check if organization name exists
    org_slug = data['organization_name'].lower().replace(' ', '').replace('-', '').replace('_', '')[:30]
    base_slug = org_slug
    counter = 1
    while Organization.query.filter_by(slug=org_slug).first():
        org_slug = f"{base_slug}{counter}"
        counter += 1
    
    # Get plan (default to Free plan)
    plan_slug = data.get('plan_slug', 'free')
    plan = SubscriptionPlan.query.filter_by(slug=plan_slug).first()
    if not plan:
        plan = SubscriptionPlan.query.filter_by(slug='free').first()
    
    try:
        # Create organization
        organization = Organization(
            name=data['organization_name'],
            slug=org_slug,
            email=data['admin_email'].strip().lower(),
            phone=data.get('phone'),
            address=data.get('address'),
            website=data.get('website'),
            industry=data.get('industry'),
            size=data.get('size', 'small'),
            plan_id=plan.id,
            subscription_status='trial',
            trial_start_date=datetime.utcnow().date(),
            trial_end_date=datetime.utcnow().date() + timedelta(days=plan.trial_days),
            employee_limit=plan.employee_limit,
            storage_limit_gb=plan.storage_limit_gb
        )
        db.session.add(organization)
        db.session.flush()  # Get the organization ID
        
        # Create admin user
        admin_user = Employee(
            organization_id=organization.id,
            employee_id='ADMIN001',
            email=data['admin_email'].strip().lower(),
            first_name=data['admin_first_name'],
            last_name=data['admin_last_name'],
            phone=data.get('admin_phone'),
            hire_date=datetime.utcnow().date(),
            position='Administrator',
            role='admin',
            status='active'
        )
        admin_user.set_password(data['admin_password'])
        db.session.add(admin_user)
        
        # Create default department
        from app.models.department import Department
        default_dept = Department(
            name='General',
            description='Default department',
            organization_id=organization.id
        )
        db.session.add(default_dept)
        
        # Update organization current employee count
        organization.current_employee_count = 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Organization registered successfully',
            'organization': organization.to_dict(),
            'admin_user': admin_user.to_dict(),
            'trial_expires_in_days': plan.trial_days
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset token"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    email = data['email'].strip().lower()
    employee = Employee.query.filter_by(email=email).first()
    
    if not employee:
        # Return success even if user doesn't exist (security best practice)
        return jsonify({'message': 'If an account with this email exists, a password reset link has been sent'}), 200
    
    # Generate reset token (in production, you'd send this via email)
    reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    # Store reset token in employee record (you might want a separate table for this)
    employee.password_reset_token = reset_token
    employee.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    employee.updated_at = datetime.utcnow()
    db.session.commit()
    
    # In production, send email here
    # For demo purposes, return the token
    return jsonify({
        'message': 'Password reset instructions sent to your email',
        'reset_token': reset_token  # Remove this in production
    }), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    
    required_fields = ['email', 'reset_token', 'new_password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    email = data['email'].strip().lower()
    employee = Employee.query.filter_by(email=email).first()
    
    if not employee:
        return jsonify({'error': 'Invalid reset token'}), 400
    
    # Check if token exists and hasn't expired
    if (not hasattr(employee, 'password_reset_token') or 
        not employee.password_reset_token or 
        employee.password_reset_token != data['reset_token']):
        return jsonify({'error': 'Invalid reset token'}), 400
    
    if (hasattr(employee, 'password_reset_expires') and 
        employee.password_reset_expires and 
        employee.password_reset_expires < datetime.utcnow()):
        return jsonify({'error': 'Reset token has expired'}), 400
    
    # Validate new password
    if len(data['new_password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Reset password
    employee.set_password(data['new_password'])
    employee.password_reset_token = None
    employee.password_reset_expires = None
    employee.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200

@bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token():
    """Validate password reset token"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('reset_token'):
        return jsonify({'error': 'Email and reset token are required'}), 400
    
    email = data['email'].strip().lower()
    employee = Employee.query.filter_by(email=email).first()
    
    if not employee:
        return jsonify({'valid': False}), 200
    
    # Check if token exists and hasn't expired
    if (not hasattr(employee, 'password_reset_token') or 
        not employee.password_reset_token or 
        employee.password_reset_token != data['reset_token']):
        return jsonify({'valid': False}), 200
    
    if (hasattr(employee, 'password_reset_expires') and 
        employee.password_reset_expires and 
        employee.password_reset_expires < datetime.utcnow()):
        return jsonify({'valid': False}), 200
    
    return jsonify({'valid': True}), 200
