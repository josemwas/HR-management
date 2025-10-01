from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.employee import Employee
from app.models.rbac import Role, Permission, EmployeeRole, RolePermission, OrganizationSetting, AuditLog
from app import db
import json

def has_permission(permission_name):
    """Decorator to check if current user has specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                if not current_user_id:
                    return jsonify({'error': 'Authentication required'}), 401
                
                employee = Employee.query.get(current_user_id)
                if not employee:
                    return jsonify({'error': 'User not found'}), 404
                
                # Super admins have all permissions
                if employee.role == 'super_admin':
                    return f(*args, **kwargs)
                
                # Check if user has the required permission
                if check_user_permission(employee, permission_name):
                    return f(*args, **kwargs)
                else:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                    
            except Exception as e:
                current_app.logger.error(f"Permission check error: {str(e)}")
                return jsonify({'error': 'Permission check failed'}), 500
        
        return decorated_function
    return decorator

def check_user_permission(employee, permission_name):
    """Check if employee has specific permission"""
    try:
        # Get all roles for the employee
        employee_roles = EmployeeRole.query.filter_by(employee_id=employee.id).all()
        
        for emp_role in employee_roles:
            role = emp_role.role
            # Check if role has the permission
            role_permission = RolePermission.query.join(Permission).filter(
                RolePermission.role_id == role.id,
                Permission.name == permission_name
            ).first()
            
            if role_permission:
                return True
        
        return False
    except Exception as e:
        current_app.logger.error(f"Permission check error: {str(e)}")
        return False

def get_user_permissions(employee):
    """Get all permissions for an employee"""
    try:
        permissions = []
        
        # Get all roles for the employee
        employee_roles = EmployeeRole.query.filter_by(employee_id=employee.id).all()
        
        for emp_role in employee_roles:
            role = emp_role.role
            for permission in role.permissions:
                if permission.name not in [p['name'] for p in permissions]:
                    permissions.append(permission.to_dict())
        
        return permissions
    except Exception as e:
        current_app.logger.error(f"Get permissions error: {str(e)}")
        return []

def assign_role_to_employee(employee_id, role_id, assigned_by_id=None, is_primary=False):
    """Assign a role to an employee"""
    try:
        # Check if assignment already exists
        existing = EmployeeRole.query.filter_by(
            employee_id=employee_id,
            role_id=role_id
        ).first()
        
        if existing:
            return False, "Role already assigned to employee"
        
        # If this is a primary role, unset other primary roles
        if is_primary:
            EmployeeRole.query.filter_by(
                employee_id=employee_id,
                is_primary=True
            ).update({'is_primary': False})
        
        # Create new role assignment
        employee_role = EmployeeRole(
            employee_id=employee_id,
            role_id=role_id,
            assigned_by=assigned_by_id,
            is_primary=is_primary
        )
        
        db.session.add(employee_role)
        db.session.commit()
        
        # Log the action
        log_audit_action(
            employee_id=assigned_by_id,
            action="assign_role",
            resource_type="employee_role",
            resource_id=employee_role.id,
            new_values=json.dumps({
                'employee_id': employee_id,
                'role_id': role_id,
                'is_primary': is_primary
            })
        )
        
        return True, "Role assigned successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Role assignment error: {str(e)}")
        return False, f"Error assigning role: {str(e)}"

def remove_role_from_employee(employee_id, role_id, removed_by_id=None):
    """Remove a role from an employee"""
    try:
        employee_role = EmployeeRole.query.filter_by(
            employee_id=employee_id,
            role_id=role_id
        ).first()
        
        if not employee_role:
            return False, "Role assignment not found"
        
        # Log the action before deletion
        log_audit_action(
            employee_id=removed_by_id,
            action="remove_role",
            resource_type="employee_role",
            resource_id=employee_role.id,
            old_values=json.dumps({
                'employee_id': employee_id,
                'role_id': role_id,
                'is_primary': employee_role.is_primary
            })
        )
        
        db.session.delete(employee_role)
        db.session.commit()
        
        return True, "Role removed successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Role removal error: {str(e)}")
        return False, f"Error removing role: {str(e)}"

def get_organization_setting(organization_id, key, default_value=None):
    """Get organization setting value"""
    try:
        setting = OrganizationSetting.query.filter_by(
            organization_id=organization_id,
            key=key
        ).first()
        
        if setting:
            return setting.get_value()
        else:
            return default_value
    except Exception as e:
        current_app.logger.error(f"Get setting error: {str(e)}")
        return default_value

def set_organization_setting(organization_id, key, value, category='general', 
                           description=None, data_type='string', is_sensitive=False, updated_by_id=None):
    """Set organization setting value"""
    try:
        setting = OrganizationSetting.query.filter_by(
            organization_id=organization_id,
            key=key
        ).first()
        
        old_value = None
        if setting:
            old_value = setting.get_value()
            setting.set_value(value)
            setting.category = category
            setting.description = description
            setting.data_type = data_type
            setting.is_sensitive = is_sensitive
        else:
            setting = OrganizationSetting(
                organization_id=organization_id,
                category=category,
                key=key,
                description=description,
                data_type=data_type,
                is_sensitive=is_sensitive
            )
            setting.set_value(value)
            db.session.add(setting)
        
        db.session.commit()
        
        # Log the action
        log_audit_action(
            employee_id=updated_by_id,
            action="update_setting",
            resource_type="organization_setting",
            resource_id=setting.id,
            old_values=json.dumps({'value': old_value}) if old_value is not None else None,
            new_values=json.dumps({'value': value})
        )
        
        return True, "Setting updated successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Set setting error: {str(e)}")
        return False, f"Error updating setting: {str(e)}"

def log_audit_action(employee_id, action, resource_type, resource_id=None, 
                    old_values=None, new_values=None, organization_id=None):
    """Log audit action"""
    try:
        if not organization_id and employee_id:
            employee = Employee.query.get(employee_id)
            if employee:
                organization_id = employee.organization_id
        
        audit_log = AuditLog(
            organization_id=organization_id,
            user_id=employee_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Audit log error: {str(e)}")

def initialize_default_permissions():
    """Initialize default system permissions"""
    default_permissions = [
        # Employee management
        {'name': 'employees.create', 'display_name': 'Create Employees', 'module': 'employees', 'action': 'create', 'description': 'Create new employee records'},
        {'name': 'employees.read', 'display_name': 'View Employees', 'module': 'employees', 'action': 'read', 'description': 'View employee information'},
        {'name': 'employees.update', 'display_name': 'Update Employees', 'module': 'employees', 'action': 'update', 'description': 'Update employee information'},
        {'name': 'employees.delete', 'display_name': 'Delete Employees', 'module': 'employees', 'action': 'delete', 'description': 'Delete employee records'},
        {'name': 'employees.manage', 'display_name': 'Manage Employees', 'module': 'employees', 'action': 'manage', 'description': 'Full employee management access'},
        
        # Attendance management
        {'name': 'attendance.create', 'display_name': 'Create Attendance', 'module': 'attendance', 'action': 'create', 'description': 'Create attendance records'},
        {'name': 'attendance.read', 'display_name': 'View Attendance', 'module': 'attendance', 'action': 'read', 'description': 'View attendance records'},
        {'name': 'attendance.update', 'display_name': 'Update Attendance', 'module': 'attendance', 'action': 'update', 'description': 'Update attendance records'},
        {'name': 'attendance.delete', 'display_name': 'Delete Attendance', 'module': 'attendance', 'action': 'delete', 'description': 'Delete attendance records'},
        {'name': 'attendance.manage', 'display_name': 'Manage Attendance', 'module': 'attendance', 'action': 'manage', 'description': 'Full attendance management access'},
        
        # Leave management
        {'name': 'leaves.create', 'display_name': 'Create Leave Requests', 'module': 'leaves', 'action': 'create', 'description': 'Create leave requests'},
        {'name': 'leaves.read', 'display_name': 'View Leave Requests', 'module': 'leaves', 'action': 'read', 'description': 'View leave requests'},
        {'name': 'leaves.update', 'display_name': 'Update Leave Requests', 'module': 'leaves', 'action': 'update', 'description': 'Update leave requests'},
        {'name': 'leaves.delete', 'display_name': 'Delete Leave Requests', 'module': 'leaves', 'action': 'delete', 'description': 'Delete leave requests'},
        {'name': 'leaves.approve', 'display_name': 'Approve Leave Requests', 'module': 'leaves', 'action': 'approve', 'description': 'Approve or reject leave requests'},
        {'name': 'leaves.manage', 'display_name': 'Manage Leave Requests', 'module': 'leaves', 'action': 'manage', 'description': 'Full leave management access'},
        
        # Payroll management
        {'name': 'payroll.create', 'display_name': 'Create Payroll', 'module': 'payroll', 'action': 'create', 'description': 'Create payroll records'},
        {'name': 'payroll.read', 'display_name': 'View Payroll', 'module': 'payroll', 'action': 'read', 'description': 'View payroll information'},
        {'name': 'payroll.update', 'display_name': 'Update Payroll', 'module': 'payroll', 'action': 'update', 'description': 'Update payroll records'},
        {'name': 'payroll.delete', 'display_name': 'Delete Payroll', 'module': 'payroll', 'action': 'delete', 'description': 'Delete payroll records'},
        {'name': 'payroll.manage', 'display_name': 'Manage Payroll', 'module': 'payroll', 'action': 'manage', 'description': 'Full payroll management access'},
        
        # Performance management
        {'name': 'performance.create', 'display_name': 'Create Performance Reviews', 'module': 'performance', 'action': 'create', 'description': 'Create performance reviews'},
        {'name': 'performance.read', 'display_name': 'View Performance Reviews', 'module': 'performance', 'action': 'read', 'description': 'View performance reviews'},
        {'name': 'performance.update', 'display_name': 'Update Performance Reviews', 'module': 'performance', 'action': 'update', 'description': 'Update performance reviews'},
        {'name': 'performance.delete', 'display_name': 'Delete Performance Reviews', 'module': 'performance', 'action': 'delete', 'description': 'Delete performance reviews'},
        {'name': 'performance.manage', 'display_name': 'Manage Performance Reviews', 'module': 'performance', 'action': 'manage', 'description': 'Full performance management access'},
        
        # Recruitment management
        {'name': 'recruitment.create', 'display_name': 'Create Job Postings', 'module': 'recruitment', 'action': 'create', 'description': 'Create job postings and manage candidates'},
        {'name': 'recruitment.read', 'display_name': 'View Recruitment', 'module': 'recruitment', 'action': 'read', 'description': 'View job postings and candidates'},
        {'name': 'recruitment.update', 'display_name': 'Update Recruitment', 'module': 'recruitment', 'action': 'update', 'description': 'Update job postings and candidate status'},
        {'name': 'recruitment.delete', 'display_name': 'Delete Recruitment', 'module': 'recruitment', 'action': 'delete', 'description': 'Delete job postings'},
        {'name': 'recruitment.manage', 'display_name': 'Manage Recruitment', 'module': 'recruitment', 'action': 'manage', 'description': 'Full recruitment management access'},
        
        # Department management
        {'name': 'departments.create', 'display_name': 'Create Departments', 'module': 'departments', 'action': 'create', 'description': 'Create new departments'},
        {'name': 'departments.read', 'display_name': 'View Departments', 'module': 'departments', 'action': 'read', 'description': 'View department information'},
        {'name': 'departments.update', 'display_name': 'Update Departments', 'module': 'departments', 'action': 'update', 'description': 'Update department information'},
        {'name': 'departments.delete', 'display_name': 'Delete Departments', 'module': 'departments', 'action': 'delete', 'description': 'Delete departments'},
        {'name': 'departments.manage', 'display_name': 'Manage Departments', 'module': 'departments', 'action': 'manage', 'description': 'Full department management access'},
        
        # Role and permission management
        {'name': 'roles.create', 'display_name': 'Create Roles', 'module': 'roles', 'action': 'create', 'description': 'Create new roles'},
        {'name': 'roles.read', 'display_name': 'View Roles', 'module': 'roles', 'action': 'read', 'description': 'View roles and permissions'},
        {'name': 'roles.update', 'display_name': 'Update Roles', 'module': 'roles', 'action': 'update', 'description': 'Update roles and permissions'},
        {'name': 'roles.delete', 'display_name': 'Delete Roles', 'module': 'roles', 'action': 'delete', 'description': 'Delete custom roles'},
        {'name': 'roles.manage', 'display_name': 'Manage Roles', 'module': 'roles', 'action': 'manage', 'description': 'Full role and permission management'},
        
        # Organization settings
        {'name': 'settings.read', 'display_name': 'View Settings', 'module': 'settings', 'action': 'read', 'description': 'View organization settings'},
        {'name': 'settings.update', 'display_name': 'Update Settings', 'module': 'settings', 'action': 'update', 'description': 'Update organization settings'},
        {'name': 'settings.manage', 'display_name': 'Manage Settings', 'module': 'settings', 'action': 'manage', 'description': 'Full settings management access'},
        
        # Reports and analytics
        {'name': 'reports.read', 'display_name': 'View Reports', 'module': 'reports', 'action': 'read', 'description': 'View reports and analytics'},
        {'name': 'reports.create', 'display_name': 'Create Reports', 'module': 'reports', 'action': 'create', 'description': 'Create custom reports'},
        {'name': 'reports.manage', 'display_name': 'Manage Reports', 'module': 'reports', 'action': 'manage', 'description': 'Full reports management access'},
        
        # System administration
        {'name': 'system.manage', 'display_name': 'System Administration', 'module': 'system', 'action': 'manage', 'description': 'Full system administration access'},
        {'name': 'audit.read', 'display_name': 'View Audit Logs', 'module': 'audit', 'action': 'read', 'description': 'View system audit logs'},
    ]
    
    try:
        for perm_data in default_permissions:
            existing = Permission.query.filter_by(name=perm_data['name']).first()
            if not existing:
                permission = Permission(**perm_data)
                db.session.add(permission)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Initialize permissions error: {str(e)}")
        return False

def initialize_default_roles(organization_id):
    """Initialize default roles for an organization"""
    default_roles = [
        {
            'name': 'admin',
            'display_name': 'Administrator',
            'description': 'Full access to all organization features',
            'is_system_role': True,
            'permissions': [
                'employees.manage', 'attendance.manage', 'leaves.manage', 'payroll.manage',
                'performance.manage', 'recruitment.manage', 'departments.manage',
                'roles.manage', 'settings.manage', 'reports.manage', 'audit.read'
            ]
        },
        {
            'name': 'manager',
            'display_name': 'Manager',
            'description': 'Management access with team oversight',
            'is_system_role': True,
            'permissions': [
                'employees.read', 'employees.update', 'attendance.read', 'attendance.update',
                'leaves.read', 'leaves.approve', 'payroll.read', 'performance.read',
                'performance.create', 'performance.update', 'recruitment.read',
                'departments.read', 'reports.read'
            ]
        },
        {
            'name': 'hr',
            'display_name': 'HR Specialist',
            'description': 'Human resources specialist with employee management access',
            'is_system_role': True,
            'permissions': [
                'employees.create', 'employees.read', 'employees.update',
                'attendance.read', 'leaves.read', 'leaves.approve',
                'recruitment.manage', 'performance.read', 'departments.read',
                'reports.read'
            ]
        },
        {
            'name': 'employee',
            'display_name': 'Employee',
            'description': 'Basic employee access to personal information',
            'is_system_role': True,
            'permissions': [
                'employees.read', 'attendance.create', 'attendance.read',
                'leaves.create', 'leaves.read', 'performance.read'
            ]
        }
    ]
    
    try:
        for role_data in default_roles:
            permissions_list = role_data.pop('permissions', [])
            
            existing_role = Role.query.filter_by(
                organization_id=organization_id,
                name=role_data['name']
            ).first()
            
            if not existing_role:
                role = Role(organization_id=organization_id, **role_data)
                db.session.add(role)
                db.session.flush()  # To get the role ID
                
                # Assign permissions to role
                for perm_name in permissions_list:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role_permission = RolePermission(
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        db.session.add(role_permission)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Initialize roles error: {str(e)}")
        return False