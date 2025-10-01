#!/usr/bin/env python3
"""
Initialize default RBAC permissions and roles for organizations.
This script should be run after setting up RBAC models to create default permissions and roles.
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.rbac import Role, Permission, RolePermission, OrganizationSetting
from app.models.organization import Organization
from app.models.employee import Employee
from app.utils.permissions import assign_role_to_employee
from sqlalchemy import text

def init_default_permissions():
    """Initialize default permissions in the database."""
    
    default_permissions = [
        # Employee Management
        {'name': 'view_employees', 'display_name': 'View Employees', 'module': 'employees', 'action': 'read', 'description': 'View employee information'},
        {'name': 'create_employees', 'display_name': 'Create Employees', 'module': 'employees', 'action': 'create', 'description': 'Create new employees'},
        {'name': 'edit_employees', 'display_name': 'Edit Employees', 'module': 'employees', 'action': 'update', 'description': 'Edit employee information'},
        {'name': 'delete_employees', 'display_name': 'Delete Employees', 'module': 'employees', 'action': 'delete', 'description': 'Delete employees'},
        {'name': 'manage_employee_roles', 'display_name': 'Manage Employee Roles', 'module': 'employees', 'action': 'manage', 'description': 'Assign roles to employees'},
        
        # Attendance Management
        {'name': 'view_attendance', 'display_name': 'View Attendance', 'module': 'attendance', 'action': 'read', 'description': 'View attendance records'},
        {'name': 'manage_attendance', 'display_name': 'Manage Attendance', 'module': 'attendance', 'action': 'manage', 'description': 'Create and edit attendance records'},
        {'name': 'approve_attendance', 'display_name': 'Approve Attendance', 'module': 'attendance', 'action': 'approve', 'description': 'Approve attendance modifications'},
        {'name': 'view_all_attendance', 'display_name': 'View All Attendance', 'module': 'attendance', 'action': 'read', 'description': 'View all employees attendance'},
        
        # Leave Management
        {'name': 'view_leaves', 'display_name': 'View Leaves', 'module': 'leaves', 'action': 'read', 'description': 'View leave requests'},
        {'name': 'create_leave_request', 'display_name': 'Create Leave Request', 'module': 'leaves', 'action': 'create', 'description': 'Create leave requests'},
        {'name': 'approve_leaves', 'display_name': 'Approve Leaves', 'module': 'leaves', 'action': 'approve', 'description': 'Approve or reject leave requests'},
        {'name': 'cancel_leaves', 'display_name': 'Cancel Leaves', 'module': 'leaves', 'action': 'delete', 'description': 'Cancel leave requests'},
        {'name': 'view_all_leaves', 'display_name': 'View All Leaves', 'module': 'leaves', 'action': 'read', 'description': 'View all employees leave requests'},
        
        # Payroll Management
        {'name': 'view_payroll', 'display_name': 'View Payroll', 'module': 'payroll', 'action': 'read', 'description': 'View payroll information'},
        {'name': 'manage_payroll', 'display_name': 'Manage Payroll', 'module': 'payroll', 'action': 'manage', 'description': 'Create and edit payroll records'},
        {'name': 'process_payroll', 'display_name': 'Process Payroll', 'module': 'payroll', 'action': 'execute', 'description': 'Process payroll payments'},
        {'name': 'view_all_payroll', 'display_name': 'View All Payroll', 'module': 'payroll', 'action': 'read', 'description': 'View all employees payroll'},
        
        # Performance Management
        {'name': 'view_performance', 'display_name': 'View Performance', 'module': 'performance', 'action': 'read', 'description': 'View performance reviews'},
        {'name': 'create_performance_review', 'display_name': 'Create Performance Review', 'module': 'performance', 'action': 'create', 'description': 'Create performance reviews'},
        {'name': 'conduct_performance_review', 'display_name': 'Conduct Performance Review', 'module': 'performance', 'action': 'execute', 'description': 'Conduct performance reviews'},
        {'name': 'view_all_performance', 'display_name': 'View All Performance', 'module': 'performance', 'action': 'read', 'description': 'View all performance reviews'},
        
        # Recruitment Management
        {'name': 'view_recruitment', 'display_name': 'View Recruitment', 'module': 'recruitment', 'action': 'read', 'description': 'View job postings and applications'},
        {'name': 'manage_job_postings', 'display_name': 'Manage Job Postings', 'module': 'recruitment', 'action': 'manage', 'description': 'Create and edit job postings'},
        {'name': 'manage_applications', 'display_name': 'Manage Applications', 'module': 'recruitment', 'action': 'manage', 'description': 'Review and process applications'},
        {'name': 'conduct_interviews', 'display_name': 'Conduct Interviews', 'module': 'recruitment', 'action': 'execute', 'description': 'Schedule and conduct interviews'},
        
        # Training Management
        {'name': 'view_training', 'display_name': 'View Training', 'module': 'training', 'action': 'read', 'description': 'View training programs and records'},
        {'name': 'create_training', 'display_name': 'Create Training', 'module': 'training', 'action': 'create', 'description': 'Create training programs'},
        {'name': 'manage_training', 'display_name': 'Manage Training', 'module': 'training', 'action': 'manage', 'description': 'Manage training programs and enrollments'},
        {'name': 'track_training_progress', 'display_name': 'Track Training Progress', 'module': 'training', 'action': 'read', 'description': 'Track employee training progress'},
        
        # Benefits Management
        {'name': 'view_benefits', 'display_name': 'View Benefits', 'module': 'benefits', 'action': 'read', 'description': 'View benefits information'},
        {'name': 'manage_benefits', 'display_name': 'Manage Benefits', 'module': 'benefits', 'action': 'manage', 'description': 'Manage employee benefits'},
        {'name': 'enroll_in_benefits', 'display_name': 'Enroll in Benefits', 'module': 'benefits', 'action': 'create', 'description': 'Enroll in benefit programs'},
        
        # Document Management
        {'name': 'view_documents', 'display_name': 'View Documents', 'module': 'documents', 'action': 'read', 'description': 'View documents'},
        {'name': 'upload_documents', 'display_name': 'Upload Documents', 'module': 'documents', 'action': 'create', 'description': 'Upload documents'},
        {'name': 'manage_documents', 'display_name': 'Manage Documents', 'module': 'documents', 'action': 'manage', 'description': 'Manage all documents'},
        {'name': 'delete_documents', 'display_name': 'Delete Documents', 'module': 'documents', 'action': 'delete', 'description': 'Delete documents'},
        
        # System Administration
        {'name': 'view_organization_settings', 'display_name': 'View Organization Settings', 'module': 'admin', 'action': 'read', 'description': 'View organization settings'},
        {'name': 'manage_organization_settings', 'display_name': 'Manage Organization Settings', 'module': 'admin', 'action': 'manage', 'description': 'Modify organization settings'},
        {'name': 'view_roles_permissions', 'display_name': 'View Roles & Permissions', 'module': 'admin', 'action': 'read', 'description': 'View roles and permissions'},
        {'name': 'manage_roles_permissions', 'display_name': 'Manage Roles & Permissions', 'module': 'admin', 'action': 'manage', 'description': 'Manage roles and permissions'},
        {'name': 'view_audit_logs', 'display_name': 'View Audit Logs', 'module': 'admin', 'action': 'read', 'description': 'View system audit logs'},
        {'name': 'manage_departments', 'display_name': 'Manage Departments', 'module': 'admin', 'action': 'manage', 'description': 'Manage organizational departments'},
        
        # Reports and Analytics
        {'name': 'view_reports', 'display_name': 'View Reports', 'module': 'reports', 'action': 'read', 'description': 'View standard reports'},
        {'name': 'create_custom_reports', 'display_name': 'Create Custom Reports', 'module': 'reports', 'action': 'create', 'description': 'Create custom reports'},
        {'name': 'export_data', 'display_name': 'Export Data', 'module': 'reports', 'action': 'export', 'description': 'Export data and reports'},
        
        # API Access
        {'name': 'api_access', 'display_name': 'API Access', 'module': 'api', 'action': 'read', 'description': 'Access API endpoints'},
        {'name': 'api_admin', 'display_name': 'API Admin', 'module': 'api', 'action': 'manage', 'description': 'Administrative API access'},
    ]
    
    print("Initializing default permissions...")
    
    created_count = 0
    for perm_data in default_permissions:
        existing = Permission.query.filter_by(name=perm_data['name']).first()
        if not existing:
            permission = Permission(
                name=perm_data['name'],
                display_name=perm_data['display_name'],
                module=perm_data['module'],
                action=perm_data['action'],
                description=perm_data['description']
            )
            db.session.add(permission)
            created_count += 1
    
    db.session.commit()
    print(f"Created {created_count} new permissions.")

def init_default_roles():
    """Initialize default roles for organizations."""
    
    default_roles = [
        {
            'name': 'Super Admin',
            'description': 'Full system access with all permissions',
            'is_system_role': True,
            'permissions': '*'  # All permissions
        },
        {
            'name': 'HR Admin',
            'description': 'Full HR management access',
            'is_system_role': True,
            'permissions': [
                'view_employees', 'create_employees', 'edit_employees', 'delete_employees',
                'view_attendance', 'manage_attendance', 'approve_attendance', 'view_all_attendance',
                'view_leaves', 'approve_leaves', 'cancel_leaves', 'view_all_leaves',
                'view_payroll', 'manage_payroll', 'process_payroll', 'view_all_payroll',
                'view_performance', 'create_performance_review', 'view_all_performance',
                'view_recruitment', 'manage_job_postings', 'manage_applications', 'conduct_interviews',
                'view_training', 'create_training', 'manage_training', 'track_training_progress',
                'view_benefits', 'manage_benefits',
                'view_documents', 'upload_documents', 'manage_documents',
                'manage_departments', 'view_reports', 'export_data'
            ]
        },
        {
            'name': 'Manager',
            'description': 'Team management with approval permissions',
            'is_system_role': True,
            'permissions': [
                'view_employees', 'edit_employees',
                'view_attendance', 'approve_attendance', 'view_all_attendance',
                'view_leaves', 'approve_leaves', 'view_all_leaves',
                'view_payroll', 'view_all_payroll',
                'view_performance', 'create_performance_review', 'conduct_performance_review', 'view_all_performance',
                'view_recruitment', 'conduct_interviews',
                'view_training', 'track_training_progress',
                'view_benefits',
                'view_documents', 'upload_documents',
                'view_reports'
            ]
        },
        {
            'name': 'HR Specialist',
            'description': 'HR operations without administrative access',
            'is_system_role': True,
            'permissions': [
                'view_employees', 'create_employees', 'edit_employees',
                'view_attendance', 'manage_attendance',
                'view_leaves', 'view_all_leaves',
                'view_payroll', 'manage_payroll',
                'view_performance', 'create_performance_review',
                'view_recruitment', 'manage_job_postings', 'manage_applications',
                'view_training', 'create_training', 'manage_training',
                'view_benefits', 'manage_benefits',
                'view_documents', 'upload_documents',
                'view_reports'
            ]
        },
        {
            'name': 'Employee',
            'description': 'Basic employee access to personal information',
            'is_system_role': True,
            'permissions': [
                'view_employees',  # Own profile only
                'view_attendance',  # Own attendance only
                'create_leave_request', 'view_leaves',  # Own leaves only
                'view_payroll',  # Own payroll only
                'view_performance',  # Own performance only
                'view_training',  # Own training only
                'enroll_in_benefits', 'view_benefits',  # Own benefits only
                'view_documents', 'upload_documents'  # Own documents only
            ]
        },
        {
            'name': 'Recruiter',
            'description': 'Recruitment and hiring focused role',
            'is_system_role': True,
            'permissions': [
                'view_employees',
                'view_recruitment', 'manage_job_postings', 'manage_applications', 'conduct_interviews',
                'view_documents', 'upload_documents',
                'view_reports'
            ]
        },
        {
            'name': 'Payroll Specialist',
            'description': 'Payroll processing and benefits management',
            'is_system_role': True,
            'permissions': [
                'view_employees',
                'view_attendance', 'view_all_attendance',
                'view_payroll', 'manage_payroll', 'process_payroll', 'view_all_payroll',
                'view_benefits', 'manage_benefits',
                'view_documents', 'upload_documents',
                'view_reports', 'export_data'
            ]
        }
    ]
    
    print("Initializing default roles...")
    
    # Get all permissions for role assignment
    all_permissions = Permission.query.all()
    permission_map = {perm.name: perm for perm in all_permissions}
    
    created_count = 0
    
    for role_data in default_roles:
        existing = Role.query.filter_by(name=role_data['name']).first()
        if not existing:
            role = Role(
                name=role_data['name'],
                display_name=role_data['name'],  # Use same as name for now
                description=role_data['description'],
                is_system_role=role_data.get('is_system_role', False)
            )
            db.session.add(role)
            db.session.flush()  # Get the role ID
            
            # Assign permissions
            if role_data['permissions'] == '*':
                # Assign all permissions
                for permission in all_permissions:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    db.session.add(role_perm)
            else:
                # Assign specific permissions
                for perm_name in role_data['permissions']:
                    if perm_name in permission_map:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=permission_map[perm_name].id
                        )
                        db.session.add(role_perm)
            
            created_count += 1
    
    db.session.commit()
    print(f"Created {created_count} new roles.")

def init_default_organization_settings():
    """Initialize default organization settings."""
    
    default_settings = [
        # General Settings
        {'key': 'organization_name', 'value': 'My Organization', 'category': 'general', 'data_type': 'string', 'description': 'Organization name'},
        {'key': 'primary_color', 'value': '#667eea', 'category': 'general', 'data_type': 'string', 'description': 'Primary brand color'},
        {'key': 'timezone', 'value': 'UTC', 'category': 'general', 'data_type': 'string', 'description': 'Default timezone'},
        {'key': 'date_format', 'value': 'YYYY-MM-DD', 'category': 'general', 'data_type': 'string', 'description': 'Date format'},
        {'key': 'currency', 'value': 'USD', 'category': 'general', 'data_type': 'string', 'description': 'Default currency'},
        
        # Attendance Settings
        {'key': 'standard_work_hours', 'value': 8, 'category': 'attendance', 'data_type': 'integer', 'description': 'Standard work hours per day'},
        {'key': 'grace_period_minutes', 'value': 15, 'category': 'attendance', 'data_type': 'integer', 'description': 'Grace period for late arrival'},
        {'key': 'require_gps_checkin', 'value': False, 'category': 'attendance', 'data_type': 'boolean', 'description': 'Require GPS for check-in'},
        {'key': 'auto_checkout', 'value': True, 'category': 'attendance', 'data_type': 'boolean', 'description': 'Auto checkout after work hours'},
        
        # Leave Settings
        {'key': 'annual_leave_days', 'value': 20, 'category': 'leaves', 'data_type': 'integer', 'description': 'Annual leave days allocation'},
        {'key': 'sick_leave_days', 'value': 10, 'category': 'leaves', 'data_type': 'integer', 'description': 'Sick leave days allocation'},
        {'key': 'personal_leave_days', 'value': 5, 'category': 'leaves', 'data_type': 'integer', 'description': 'Personal leave days allocation'},
        {'key': 'require_manager_approval', 'value': True, 'category': 'leaves', 'data_type': 'boolean', 'description': 'Require manager approval for leaves'},
        {'key': 'advance_notice_days', 'value': 7, 'category': 'leaves', 'data_type': 'integer', 'description': 'Advance notice required for leaves'},
        
        # Security Settings
        {'key': 'enable_two_factor', 'value': False, 'category': 'security', 'data_type': 'boolean', 'description': 'Enable two-factor authentication'},
        {'key': 'session_timeout_minutes', 'value': 480, 'category': 'security', 'data_type': 'integer', 'description': 'Session timeout in minutes'},
        {'key': 'password_policy', 'value': json.dumps({'min_length': 8, 'require_uppercase': True, 'require_numbers': True, 'require_special_chars': False}), 'category': 'security', 'data_type': 'json', 'description': 'Password policy requirements'},
        
        # Notification Settings
        {'key': 'email_notifications', 'value': True, 'category': 'notifications', 'data_type': 'boolean', 'description': 'Enable email notifications'},
        {'key': 'sms_notifications', 'value': False, 'category': 'notifications', 'data_type': 'boolean', 'description': 'Enable SMS notifications'},
    ]
    
    print("Initializing default organization settings...")
    
    # Get all organizations to apply settings to
    organizations = Organization.query.all()
    
    if not organizations:
        print("No organizations found. Skipping organization settings initialization.")
        return
    
    created_count = 0
    
    for org in organizations:
        print(f"Initializing settings for organization: {org.name}")
        
        for setting_data in default_settings:
            existing = OrganizationSetting.query.filter_by(
                organization_id=org.id,
                key=setting_data['key']
            ).first()
            
            if not existing:
                setting = OrganizationSetting(
                    organization_id=org.id,
                    key=setting_data['key'],
                    value=setting_data['value'],
                    category=setting_data['category'],
                    data_type=setting_data['data_type'],
                    description=setting_data['description']
                )
                db.session.add(setting)
                created_count += 1
    
    db.session.commit()
    print(f"Created {created_count} organization settings.")

def assign_admin_roles():
    """Assign admin roles to existing users."""
    
    print("Assigning admin roles to existing users...")
    
    # Find organizations
    organizations = Organization.query.all()
    
    if not organizations:
        print("No organizations found. Skipping role assignments.")
        return
    
    # Get the Super Admin role
    super_admin_role = Role.query.filter_by(name='Super Admin').first()
    if not super_admin_role:
        print("Super Admin role not found. Cannot assign roles.")
        return
    
    assigned_count = 0
    
    for org in organizations:
        # Find admin users in this organization
        admin_employees = Employee.query.filter_by(
            organization_id=org.id,
            role='admin'
        ).all()
        
        for employee in admin_employees:
            try:
                assign_role_to_employee(employee.id, super_admin_role.id)
                assigned_count += 1
                print(f"Assigned Super Admin role to {employee.first_name} {employee.last_name} in {org.name}")
            except Exception as e:
                print(f"Failed to assign role to {employee.first_name} {employee.last_name}: {str(e)}")
    
    print(f"Assigned roles to {assigned_count} employees.")

def main():
    """Main initialization function."""
    
    print("Starting RBAC initialization...")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize permissions first
            init_default_permissions()
            
            # Then initialize roles (which depend on permissions)
            init_default_roles()
            
            # Initialize organization settings
            init_default_organization_settings()
            
            # Assign admin roles to existing users
            assign_admin_roles()
            
            print("=" * 50)
            print("RBAC initialization completed successfully!")
            print("\nNext steps:")
            print("1. Review and customize roles and permissions as needed")
            print("2. Assign appropriate roles to employees")
            print("3. Configure organization settings through the admin interface")
            print("4. Test the permission system with different user roles")
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)