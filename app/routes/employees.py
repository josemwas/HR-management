from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.leave import Leave
from datetime import datetime, date

bp = Blueprint('employees', __name__, url_prefix='/api/employees')

@bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """Get dashboard statistics for the current organization"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get counts for the current organization
        employee_count = Employee.query.filter_by(
            organization_id=employee.organization_id,
            status='active'
        ).count()
        
        department_count = Department.query.filter_by(
            organization_id=employee.organization_id
        ).count()
        
        # Get today's attendance count
        today = date.today()
        attendance_today = Attendance.query.join(Employee).filter(
            Employee.organization_id == employee.organization_id,
            Attendance.date == today,
            Attendance.status == 'present'
        ).count()
        
        # Get pending leaves count
        pending_leaves = Leave.query.join(Employee).filter(
            Employee.organization_id == employee.organization_id,
            Leave.status == 'pending'
        ).count()
        
        return jsonify({
            'employee_count': employee_count,
            'department_count': department_count,
            'attendance_today': attendance_today,
            'pending_leaves': pending_leaves
        })
        
    except Exception as e:
        return jsonify({
            'employee_count': 0,
            'department_count': 0,
            'attendance_today': 0,
            'pending_leaves': 0
        })

@bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees with advanced filtering"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee:
        return jsonify({'error': 'Unauthorized'}), 401
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    status = request.args.get('status', None)
    department_id = request.args.get('department_id', None, type=int)
    role = request.args.get('role', None)
    search = request.args.get('search', None)
    simple = request.args.get('simple', 'true')
    
    query = Employee.query
    
    # Filter by organization if multi-tenant
    if hasattr(employee, 'organization_id') and employee.organization_id:
        query = query.filter_by(organization_id=employee.organization_id)
    
    if status:
        query = query.filter_by(status=status)
    if department_id:
        query = query.filter_by(department_id=department_id)
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(f'%{search}%'),
                Employee.last_name.ilike(f'%{search}%'),
                Employee.email.ilike(f'%{search}%'),
                Employee.employee_id.ilike(f'%{search}%')
            )
        )
    
    if simple == 'true':
        employees = query.all()
        return jsonify([emp.to_dict() for emp in employees]), 200
    else:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'employees': [emp.to_dict() for emp in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200

@bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get employee by ID with detailed information"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee:
        return jsonify({'error': 'Unauthorized'}), 401
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Check if employee belongs to user's organization
    if hasattr(current_employee, 'organization_id') and hasattr(employee, 'organization_id'):
        if current_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Get additional employee details
    employee_data = employee.to_dict()
    
    # Add department information
    if employee.department:
        employee_data['department_name'] = employee.department.name
        if employee.department.manager_id:
            manager = Employee.query.get(employee.department.manager_id)
            if manager:
                employee_data['department_manager'] = f"{manager.first_name} {manager.last_name}"
    
    # Add employment duration
    from datetime import date
    if employee.hire_date:
        employment_days = (date.today() - employee.hire_date).days
        employee_data['employment_duration_days'] = employment_days
        employee_data['employment_duration_years'] = round(employment_days / 365.25, 1)
    
    # Add recent activity summary (if user has permission)
    if current_employee.role in ['admin', 'manager'] or current_employee.id == employee.id:
        # Add attendance summary (last 30 days)
        from app.models.attendance import Attendance
        from datetime import timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        
        attendance_count = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            Attendance.date >= thirty_days_ago
        ).count()
        employee_data['recent_attendance_days'] = attendance_count
        
        # Add leave summary
        from app.models.leave import Leave
        pending_leaves = Leave.query.filter(
            Leave.employee_id == employee.id,
            Leave.status == 'pending'
        ).count()
        employee_data['pending_leave_requests'] = pending_leaves
    
    return jsonify(employee_data), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_employee():
    """Create new employee with enhanced validation"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    required_fields = ['employee_id', 'email', 'first_name', 'last_name', 'hire_date', 'position']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Enhanced validation
    existing_query = Employee.query.filter_by(employee_id=data['employee_id'])
    if hasattr(current_employee, 'organization_id') and current_employee.organization_id:
        existing_query = existing_query.filter_by(organization_id=current_employee.organization_id)
    
    if existing_query.first():
        return jsonify({'error': 'Employee ID already exists in this organization'}), 400
    
    email_query = Employee.query.filter_by(email=data['email'])
    if hasattr(current_employee, 'organization_id') and current_employee.organization_id:
        email_query = email_query.filter_by(organization_id=current_employee.organization_id)
    
    if email_query.first():
        return jsonify({'error': 'Email already exists in this organization'}), 400
    
    # Validate department
    if data.get('department_id'):
        dept = Department.query.get(data['department_id'])
        if not dept:
            return jsonify({'error': 'Department not found'}), 400
        if hasattr(current_employee, 'organization_id') and hasattr(dept, 'organization_id'):
            if current_employee.organization_id != dept.organization_id:
                return jsonify({'error': 'Department not in your organization'}), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate salary if provided
    if data.get('salary') and data['salary'] < 0:
        return jsonify({'error': 'Salary cannot be negative'}), 400
    
    employee = Employee(
        employee_id=data['employee_id'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
        hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
        position=data['position'],
        department_id=data.get('department_id'),
        salary=data.get('salary'),
        status=data.get('status', 'active'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        role=data.get('role', 'employee')
    )
    
    # Set organization_id if current employee has one
    if hasattr(current_employee, 'organization_id') and current_employee.organization_id:
        employee.organization_id = current_employee.organization_id
    
    if data.get('password'):
        employee.set_password(data['password'])
    
    db.session.add(employee)
    
    # Update organization employee count if applicable
    if hasattr(current_employee, 'organization') and current_employee.organization:
        current_employee.organization.current_employee_count = Employee.query.filter_by(
            organization_id=current_employee.organization_id
        ).count() + 1
    
    db.session.commit()
    
    return jsonify(employee.to_dict()), 201

@bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update employee with enhanced validation and security"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee:
        return jsonify({'error': 'User not found'}), 404
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Enhanced authorization checks
    can_edit = False
    
    # Super admin can edit anyone
    if current_employee.role == 'super_admin':
        can_edit = True
    # Admin can edit anyone in their organization
    elif current_employee.role == 'admin':
        if hasattr(current_employee, 'organization_id') and hasattr(employee, 'organization_id'):
            can_edit = current_employee.organization_id == employee.organization_id
        else:
            can_edit = True  # Fallback for non-SaaS mode
    # Manager can edit employees in their department or organization
    elif current_employee.role == 'manager':
        if hasattr(current_employee, 'organization_id') and hasattr(employee, 'organization_id'):
            if current_employee.organization_id == employee.organization_id:
                # Check if manager is department head or managing this employee
                if (current_employee.department_id == employee.department_id or
                    current_employee.managed_departments or
                    employee.manager_id == current_employee.id):
                    can_edit = True
        else:
            can_edit = current_employee.department_id == employee.department_id
    # Employee can edit their own profile (limited fields)
    elif current_employee_id == employee_id:
        can_edit = True
    
    if not can_edit:
        return jsonify({'error': 'Insufficient permissions to edit this employee'}), 403
    
    data = request.get_json()
    
    # Define editable fields based on role
    if current_employee.role in ['super_admin', 'admin']:
        # Admin can edit all fields
        editable_fields = [
            'email', 'first_name', 'last_name', 'phone', 'date_of_birth',
            'position', 'department_id', 'salary', 'status', 'address',
            'emergency_contact', 'role', 'manager_id'
        ]
    elif current_employee.role == 'manager':
        # Manager can edit most fields except role and salary (depending on company policy)
        editable_fields = [
            'email', 'first_name', 'last_name', 'phone', 'date_of_birth',
            'position', 'department_id', 'address', 'emergency_contact', 'manager_id'
        ]
    else:
        # Employee can only edit personal information
        editable_fields = [
            'phone', 'address', 'emergency_contact'
        ]
    
    # Enhanced validation
    if 'email' in data and 'email' in editable_fields:
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check for email uniqueness within organization
        email_query = Employee.query.filter_by(email=data['email']).filter(Employee.id != employee_id)
        if hasattr(employee, 'organization_id') and employee.organization_id:
            email_query = email_query.filter_by(organization_id=employee.organization_id)
        
        if email_query.first():
            return jsonify({'error': 'Email already exists in this organization'}), 400
    
    if 'department_id' in data and 'department_id' in editable_fields:
        if data['department_id']:
            dept = Department.query.get(data['department_id'])
            if not dept:
                return jsonify({'error': 'Department not found'}), 400
            if hasattr(employee, 'organization_id') and hasattr(dept, 'organization_id'):
                if employee.organization_id != dept.organization_id:
                    return jsonify({'error': 'Department not in your organization'}), 400
    
    if 'salary' in data and 'salary' in editable_fields:
        if data['salary'] < 0:
            return jsonify({'error': 'Salary cannot be negative'}), 400
    
    if 'manager_id' in data and 'manager_id' in editable_fields:
        if data['manager_id']:
            manager = Employee.query.get(data['manager_id'])
            if not manager:
                return jsonify({'error': 'Manager not found'}), 400
            if hasattr(employee, 'organization_id') and hasattr(manager, 'organization_id'):
                if employee.organization_id != manager.organization_id:
                    return jsonify({'error': 'Manager not in your organization'}), 400
            if manager.role not in ['admin', 'manager']:
                return jsonify({'error': 'Selected manager does not have management role'}), 400
    
    # Update allowed fields
    updated_fields = []
    for field in editable_fields:
        if field in data:
            if field in ['date_of_birth', 'hire_date'] and data[field]:
                setattr(employee, field, datetime.strptime(data[field], '%Y-%m-%d').date())
            else:
                setattr(employee, field, data[field])
            updated_fields.append(field)
    
    # Handle password update (only if user has permission)
    if 'password' in data and (current_employee.role in ['super_admin', 'admin'] or current_employee_id == employee_id):
        if len(data['password']) >= 6:
            employee.set_password(data['password'])
            updated_fields.append('password')
        else:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    employee.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Employee updated successfully',
        'updated_fields': updated_fields,
        'employee': employee.to_dict()
    }), 200

@bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Delete employee with enhanced security and organization checks"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions - only admin and super_admin can delete employees
    if current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions to delete employees'}), 403
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Prevent self-deletion
    if current_employee_id == employee_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Organization isolation check
    if (current_employee.role == 'admin' and 
        hasattr(current_employee, 'organization_id') and 
        hasattr(employee, 'organization_id')):
        if current_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Cannot delete employee from different organization'}), 403
    
    # Check if employee has dependent records
    dependencies = []
    
    # Check for attendance records
    from app.models.attendance import Attendance
    if Attendance.query.filter_by(employee_id=employee_id).first():
        dependencies.append('attendance records')
    
    # Check for leave requests
    from app.models.leave import Leave
    if Leave.query.filter_by(employee_id=employee_id).first():
        dependencies.append('leave requests')
    
    # Check for payroll records
    from app.models.payroll import Payroll
    if Payroll.query.filter_by(employee_id=employee_id).first():
        dependencies.append('payroll records')
    
    # Check for performance reviews
    from app.models.performance import Performance
    if Performance.query.filter_by(employee_id=employee_id).first():
        dependencies.append('performance reviews')
    
    # Check if employee is a manager of others
    managed_employees = Employee.query.filter_by(manager_id=employee_id).all()
    if managed_employees:
        dependencies.append(f'{len(managed_employees)} subordinate employees')
    
    # If there are dependencies, offer soft delete option
    if dependencies and request.args.get('force') != 'true':
        return jsonify({
            'error': 'Cannot delete employee due to existing dependencies',
            'dependencies': dependencies,
            'suggestion': 'Consider setting status to "inactive" instead',
            'force_delete_url': f'/api/employees/{employee_id}?force=true'
        }), 400
    
    try:
        # If force delete is requested, handle dependencies
        if dependencies and request.args.get('force') == 'true':
            # Update managed employees to remove manager reference
            for managed_emp in managed_employees:
                managed_emp.manager_id = None
            
            # Note: For other dependencies, you might want to cascade delete
            # or transfer ownership depending on business requirements
        
        # Update organization employee count if applicable
        if hasattr(employee, 'organization') and employee.organization:
            employee.organization.current_employee_count = Employee.query.filter_by(
                organization_id=employee.organization_id
            ).count() - 1
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'message': 'Employee deleted successfully',
            'deleted_employee_id': employee_id,
            'dependencies_handled': dependencies if request.args.get('force') == 'true' else []
        }), 200
        
    except Exception as e:
        db.session.rollback()
# Security and audit endpoints

@bp.route('/security/audit-log', methods=['GET'])
@jwt_required()
def get_audit_log():
    """Get security audit log for employees"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # For now, return a placeholder - in a real system, you'd have an audit table
    audit_events = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'login',
            'employee_id': current_employee_id,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
    ]
    
    return jsonify({
        'audit_log': audit_events,
        'total_events': len(audit_events)
    })

@bp.route('/security/active-sessions', methods=['GET'])
@jwt_required()
def get_active_sessions():
    """Get active user sessions (admin only)"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # This is a placeholder - in production, you'd track sessions in Redis or database
    sessions = [
        {
            'employee_id': current_employee_id,
            'email': current_employee.email,
            'login_time': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'status': 'active'
        }
    ]
    
    return jsonify({
        'active_sessions': sessions,
        'total_sessions': len(sessions)
    })

@bp.route('/security/password-policy', methods=['GET'])
@jwt_required()
def get_password_policy():
    """Get password policy requirements"""
    policy = {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special_chars': True,
        'password_expiry_days': 90,
        'password_history_count': 5,
        'max_login_attempts': 5,
        'lockout_duration_minutes': 30
    }
    
    return jsonify({'password_policy': policy})

@bp.route('/security/two-factor/setup', methods=['POST'])
@jwt_required()
def setup_two_factor():
    """Setup two-factor authentication"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee:
        return jsonify({'error': 'User not found'}), 404
    
    # This is a placeholder for 2FA setup
    # In production, you'd generate a QR code and secret key
    return jsonify({
        'message': '2FA setup initiated',
        'qr_code_url': 'placeholder_qr_code_url',
        'backup_codes': ['123456', '234567', '345678']  # Generate real backup codes
    })

@bp.route('/<int:employee_id>/security/reset-password', methods=['POST'])
@jwt_required()
def admin_reset_password(employee_id):
    """Admin reset employee password"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Organization isolation check
    if (current_employee.role == 'admin' and 
        hasattr(current_employee, 'organization_id') and 
        hasattr(employee, 'organization_id')):
        if current_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Cannot reset password for employee from different organization'}), 403
    
    # Generate temporary password
    import secrets
    import string
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    employee.set_password(temp_password)
    employee.password_reset_required = True  # Flag to force password change on next login
    employee.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Password reset successfully',
        'temporary_password': temp_password,
        'note': 'Employee must change password on next login'
    })

@bp.route('/<int:employee_id>/security/lock-account', methods=['POST'])
@jwt_required()
def lock_account(employee_id):
    """Lock employee account"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    if current_employee_id == employee_id:
        return jsonify({'error': 'Cannot lock your own account'}), 400
    
    # Organization isolation check
    if (current_employee.role == 'admin' and 
        hasattr(current_employee, 'organization_id') and 
        hasattr(employee, 'organization_id')):
        if current_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Cannot lock account from different organization'}), 403
    
    employee.status = 'locked'
    employee.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Account locked for {employee.first_name} {employee.last_name}',
        'employee_id': employee_id
    })

@bp.route('/<int:employee_id>/security/unlock-account', methods=['POST'])
@jwt_required()
def unlock_account(employee_id):
    """Unlock employee account"""
    current_employee_id = get_jwt_identity()
    current_employee = Employee.query.get(current_employee_id)
    
    if not current_employee or current_employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Organization isolation check
    if (current_employee.role == 'admin' and 
        hasattr(current_employee, 'organization_id') and 
        hasattr(employee, 'organization_id')):
        if current_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Cannot unlock account from different organization'}), 403
    
    employee.status = 'active'
    employee.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Account unlocked for {employee.first_name} {employee.last_name}',
        'employee_id': employee_id
    })

@bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments with enhanced details"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get departments for the current organization
    query = Department.query
    if hasattr(employee, 'organization_id') and employee.organization_id:
        query = query.filter_by(organization_id=employee.organization_id)
    
    departments = query.all()
    
    # Enhanced department data with employee counts and manager info
    dept_data = []
    for dept in departments:
        dept_dict = dept.to_dict()
        
        # Add manager information
        if dept.manager_id:
            manager = Employee.query.get(dept.manager_id)
            if manager:
                dept_dict['manager_name'] = f"{manager.first_name} {manager.last_name}"
                dept_dict['manager_email'] = manager.email
        
        # Add department statistics
        active_employees = Employee.query.filter_by(
            department_id=dept.id, 
            status='active'
        ).count()
        dept_dict['active_employee_count'] = active_employees
        
        # Add recent hires (last 30 days)
        from datetime import date, timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_hires = Employee.query.filter(
            Employee.department_id == dept.id,
            Employee.hire_date >= thirty_days_ago
        ).count()
        dept_dict['recent_hires'] = recent_hires
        
        dept_data.append(dept_dict)
    
    return jsonify(dept_data), 200

@bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    """Create new department with validation"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Department name is required'}), 400
    
    # Check for duplicate department name within organization
    existing_query = Department.query.filter_by(name=data['name'])
    if hasattr(employee, 'organization_id') and employee.organization_id:
        existing_query = existing_query.filter_by(organization_id=employee.organization_id)
    
    if existing_query.first():
        return jsonify({'error': 'Department name already exists'}), 400
    
    # Validate manager if provided
    manager_id = data.get('manager_id')
    if manager_id:
        manager = Employee.query.get(manager_id)
        if not manager:
            return jsonify({'error': 'Manager not found'}), 400
        if manager.role not in ['admin', 'manager']:
            return jsonify({'error': 'Selected employee cannot be a manager'}), 400
    
    department = Department(
        name=data['name'],
        description=data.get('description'),
        manager_id=manager_id
    )
    
    # Set organization_id if employee has one
    if hasattr(employee, 'organization_id') and employee.organization_id:
        department.organization_id = employee.organization_id
    
    db.session.add(department)
    db.session.commit()
    
    return jsonify(department.to_dict()), 201

@bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    """Update department details"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    department = Department.query.get_or_404(dept_id)
    data = request.get_json()
    
    # Check if department belongs to user's organization
    if hasattr(employee, 'organization_id') and hasattr(department, 'organization_id'):
        if employee.organization_id != department.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    if 'name' in data:
        # Check for duplicate name
        existing = Department.query.filter(
            Department.name == data['name'],
            Department.id != dept_id
        ).first()
        if existing:
            return jsonify({'error': 'Department name already exists'}), 400
        department.name = data['name']
    
    if 'description' in data:
        department.description = data['description']
    
    if 'manager_id' in data:
        manager_id = data['manager_id']
        if manager_id:
            manager = Employee.query.get(manager_id)
            if not manager:
                return jsonify({'error': 'Manager not found'}), 400
            if manager.role not in ['admin', 'manager']:
                return jsonify({'error': 'Selected employee cannot be a manager'}), 400
        department.manager_id = manager_id
    
    department.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(department.to_dict()), 200

@bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required()
def delete_department(dept_id):
    """Delete department with validation"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee or employee.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    department = Department.query.get_or_404(dept_id)
    
    # Check if department belongs to user's organization
    if hasattr(employee, 'organization_id') and hasattr(department, 'organization_id'):
        if employee.organization_id != department.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Check if department has employees
    employee_count = Employee.query.filter_by(department_id=dept_id).count()
    if employee_count > 0:
        return jsonify({'error': f'Cannot delete department with {employee_count} employees. Please reassign employees first.'}), 400
    
    db.session.delete(department)
    db.session.commit()
    
    return jsonify({'message': 'Department deleted successfully'}), 200

@bp.route('/departments/<int:dept_id>/employees', methods=['GET'])
@jwt_required()
def get_department_employees(dept_id):
    """Get all employees in a specific department"""
    current_employee_id = get_jwt_identity()
    employee = Employee.query.get(current_employee_id)
    
    if not employee:
        return jsonify({'error': 'Unauthorized'}), 401
    
    department = Department.query.get_or_404(dept_id)
    
    # Check if department belongs to user's organization
    if hasattr(employee, 'organization_id') and hasattr(department, 'organization_id'):
        if employee.organization_id != department.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    employees = Employee.query.filter_by(department_id=dept_id).all()
    
    return jsonify({
        'department': department.to_dict(),
        'employees': [emp.to_dict() for emp in employees]
    }), 200
