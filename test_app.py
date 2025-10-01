#!/usr/bin/env python3
"""
Test script to diagnose Flask app issues
"""
import sys
import traceback

try:
    print("Testing Flask app initialization...")
    from app import create_app
    
    print("Creating app...")
    app = create_app()
    
    print("Testing app context...")
    with app.app_context():
        # Test database connection
        from app import db
        from app.models.employee import Employee
        
        print("Testing database connection...")
        employee_count = Employee.query.count()
        print(f"Database connection OK - Found {employee_count} employees")
        
        # Test RBAC models
        from app.models.rbac import Role, Permission
        role_count = Role.query.count()
        perm_count = Permission.query.count()
        print(f"RBAC models OK - Found {role_count} roles, {perm_count} permissions")
        
        # Test routes
        print("Testing routes...")
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        key_routes = ['/roles', '/settings', '/api/rbac/roles', '/api/rbac/settings']
        
        for route in key_routes:
            status = "✓" if route in routes else "✗"
            print(f"  {status} {route}")
        
        print("\n✅ Flask app initialization: SUCCESS")
        
except Exception as e:
    print(f"\n❌ Flask app initialization: FAILED")
    print(f"Error: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)