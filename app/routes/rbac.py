from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.employee import Employee
from app.models.rbac import Role, Permission, RolePermission, EmployeeRole, OrganizationSetting, AuditLog
from app.utils.permissions import (
    has_permission, assign_role_to_employee, remove_role_from_employee,
    get_organization_setting, set_organization_setting, log_audit_action,
    get_user_permissions
)
from app import db
import json

rbac_bp = Blueprint('rbac', __name__, url_prefix='/api/rbac')

@rbac_bp.route('/roles', methods=['GET'])
@jwt_required()
@has_permission('view_roles_permissions')
def get_roles():
    """Get all roles for the organization"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee or not employee.organization_id:
            return jsonify({'error': 'Organization not found'}), 404
        
        roles = Role.query.filter_by(organization_id=employee.organization_id).all()
        
        return jsonify({
            'roles': [role.to_dict() for role in roles],
            'total': len(roles)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/roles', methods=['POST'])
@jwt_required()
@has_permission('manage_roles_permissions')
def create_role():
    """Create a new role"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee or not employee.organization_id:
            return jsonify({'error': 'Organization not found'}), 404
        
        data = request.get_json()
        if not data or not data.get('name') or not data.get('display_name'):
            return jsonify({'error': 'Name and display name are required'}), 400
        
        # Check if role name already exists
        existing = Role.query.filter_by(
            organization_id=employee.organization_id,
            name=data['name']
        ).first()
        
        if existing:
            return jsonify({'error': 'Role name already exists'}), 409
        
        # Create new role
        role = Role(
            organization_id=employee.organization_id,
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(role)
        db.session.flush()
        
        # Assign permissions if provided
        permission_ids = data.get('permission_ids', [])
        for perm_id in permission_ids:
            permission = Permission.query.get(perm_id)
            if permission:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=perm_id
                )
                db.session.add(role_permission)
        
        db.session.commit()
        
        # Log the action
        log_audit_action(
            employee_id=current_user_id,
            action="create_role",
            resource_type="role",
            resource_id=role.id,
            new_values=json.dumps(data)
        )
        
        return jsonify({
            'message': 'Role created successfully',
            'role': role.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
@has_permission('manage_roles_permissions')
def update_role(role_id):
    """Update a role"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        role = Role.query.filter_by(
            id=role_id,
            organization_id=employee.organization_id
        ).first()
        
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        if role.is_system_role:
            return jsonify({'error': 'Cannot modify system roles'}), 403
        
        data = request.get_json()
        old_values = role.to_dict()
        
        # Update basic role information
        if 'display_name' in data:
            role.display_name = data['display_name']
        if 'description' in data:
            role.description = data['description']
        if 'is_active' in data:
            role.is_active = data['is_active']
        
        # Update permissions if provided
        if 'permission_ids' in data:
            # Remove existing permissions
            RolePermission.query.filter_by(role_id=role_id).delete()
            
            # Add new permissions
            for perm_id in data['permission_ids']:
                permission = Permission.query.get(perm_id)
                if permission:
                    role_permission = RolePermission(
                        role_id=role_id,
                        permission_id=perm_id
                    )
                    db.session.add(role_permission)
        
        db.session.commit()
        
        # Log the action
        log_audit_action(
            employee_id=current_user_id,
            action="update_role",
            resource_type="role",
            resource_id=role_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(data)
        )
        
        return jsonify({
            'message': 'Role updated successfully',
            'role': role.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
@has_permission('manage_roles_permissions')
def delete_role(role_id):
    """Delete a role"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        role = Role.query.filter_by(
            id=role_id,
            organization_id=employee.organization_id
        ).first()
        
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        if role.is_system_role:
            return jsonify({'error': 'Cannot delete system roles'}), 403
        
        # Check if role is assigned to any employees
        employee_roles = EmployeeRole.query.filter_by(role_id=role_id).count()
        if employee_roles > 0:
            return jsonify({'error': 'Cannot delete role that is assigned to employees'}), 409
        
        # Log the action before deletion
        log_audit_action(
            employee_id=current_user_id,
            action="delete_role",
            resource_type="role",
            resource_id=role_id,
            old_values=json.dumps(role.to_dict())
        )
        
        # Delete role permissions first
        RolePermission.query.filter_by(role_id=role_id).delete()
        
        # Delete the role
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'message': 'Role deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/permissions', methods=['GET'])
@jwt_required()
@has_permission('view_roles_permissions')
def get_permissions():
    """Get all available permissions"""
    try:
        permissions = Permission.query.all()
        
        # Group permissions by module
        grouped_permissions = {}
        for permission in permissions:
            if permission.module not in grouped_permissions:
                grouped_permissions[permission.module] = []
            grouped_permissions[permission.module].append(permission.to_dict())
        
        return jsonify({
            'permissions': [perm.to_dict() for perm in permissions],
            'grouped_permissions': grouped_permissions,
            'total': len(permissions)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/employees/<int:employee_id>/roles', methods=['GET'])
@jwt_required()
@has_permission('view_employees')
def get_employee_roles(employee_id):
    """Get roles assigned to an employee"""
    try:
        current_user_id = get_jwt_identity()
        current_employee = Employee.query.get(current_user_id)
        
        employee = Employee.query.filter_by(
            id=employee_id,
            organization_id=current_employee.organization_id
        ).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        employee_roles = EmployeeRole.query.filter_by(employee_id=employee_id).all()
        
        return jsonify({
            'employee_roles': [er.to_dict() for er in employee_roles],
            'permissions': get_user_permissions(employee)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/employees/<int:employee_id>/roles', methods=['POST'])
@jwt_required()
@has_permission('manage_employee_roles')
def assign_employee_role(employee_id):
    """Assign a role to an employee"""
    try:
        current_user_id = get_jwt_identity()
        current_employee = Employee.query.get(current_user_id)
        
        employee = Employee.query.filter_by(
            id=employee_id,
            organization_id=current_employee.organization_id
        ).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        role_id = data.get('role_id')
        is_primary = data.get('is_primary', False)
        
        if not role_id:
            return jsonify({'error': 'Role ID is required'}), 400
        
        # Verify role belongs to organization
        role = Role.query.filter_by(
            id=role_id,
            organization_id=current_employee.organization_id
        ).first()
        
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        success, message = assign_role_to_employee(
            employee_id=employee_id,
            role_id=role_id,
            assigned_by_id=current_user_id,
            is_primary=is_primary
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/employees/<int:employee_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
@has_permission('manage_employee_roles')
def remove_employee_role(employee_id, role_id):
    """Remove a role from an employee"""
    try:
        current_user_id = get_jwt_identity()
        current_employee = Employee.query.get(current_user_id)
        
        employee = Employee.query.filter_by(
            id=employee_id,
            organization_id=current_employee.organization_id
        ).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        success, message = remove_role_from_employee(
            employee_id=employee_id,
            role_id=role_id,
            removed_by_id=current_user_id
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/settings', methods=['GET'])
@jwt_required()
@has_permission('view_organization_settings')
def get_organization_settings():
    """Get organization settings"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee or not employee.organization_id:
            return jsonify({'error': 'Organization not found'}), 404
        
        category = request.args.get('category')
        
        query = OrganizationSetting.query.filter_by(organization_id=employee.organization_id)
        if category:
            query = query.filter_by(category=category)
        
        settings = query.all()
        
        # Group settings by category
        grouped_settings = {}
        for setting in settings:
            if setting.category not in grouped_settings:
                grouped_settings[setting.category] = []
            grouped_settings[setting.category].append(setting.to_dict())
        
        return jsonify({
            'settings': [setting.to_dict() for setting in settings],
            'grouped_settings': grouped_settings,
            'total': len(settings)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/settings', methods=['POST'])
@jwt_required()
@has_permission('manage_organization_settings')
def update_organization_settings():
    """Update organization settings"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee or not employee.organization_id:
            return jsonify({'error': 'Organization not found'}), 404
        
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Settings array is required'}), 400
        
        updated_settings = []
        for setting_data in data:
            key = setting_data.get('key')
            value = setting_data.get('value')
            category = setting_data.get('category', 'general')
            description = setting_data.get('description')
            data_type = setting_data.get('data_type', 'string')
            is_sensitive = setting_data.get('is_sensitive', False)
            
            if not key:
                continue
            
            success, message = set_organization_setting(
                organization_id=employee.organization_id,
                key=key,
                value=value,
                category=category,
                description=description,
                data_type=data_type,
                is_sensitive=is_sensitive,
                updated_by_id=current_user_id
            )
            
            if success:
                updated_settings.append(key)
        
        return jsonify({
            'message': f'Updated {len(updated_settings)} settings',
            'updated_settings': updated_settings
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@has_permission('view_audit_logs')
def get_audit_logs():
    """Get audit logs for the organization"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee or not employee.organization_id:
            return jsonify({'error': 'Organization not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action = request.args.get('action')
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id', type=int)
        
        query = AuditLog.query.filter_by(organization_id=employee.organization_id)
        
        if action:
            query = query.filter(AuditLog.action.ilike(f'%{action}%'))
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        query = query.order_by(AuditLog.timestamp.desc())
        
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'audit_logs': [log.to_dict() for log in paginated.items],
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated.pages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rbac_bp.route('/my-permissions', methods=['GET'])
@jwt_required()
def get_my_permissions():
    """Get current user's permissions"""
    try:
        current_user_id = get_jwt_identity()
        employee = Employee.query.get(current_user_id)
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Super admins have all permissions
        if employee.role == 'super_admin':
            all_permissions = Permission.query.all()
            return jsonify({
                'permissions': [perm.to_dict() for perm in all_permissions],
                'is_super_admin': True
            }), 200
        
        permissions = get_user_permissions(employee)
        employee_roles = EmployeeRole.query.filter_by(employee_id=employee.id).all()
        
        return jsonify({
            'permissions': permissions,
            'roles': [er.to_dict() for er in employee_roles],
            'is_super_admin': False
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500