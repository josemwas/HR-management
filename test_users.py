from app import create_app
from app.models.employee import Employee
from app.models.rbac import Role, EmployeeRole

app = create_app()
with app.app_context():
    # Check if we have any employees
    employees = Employee.query.limit(5).all()
    print('Sample employees:')
    for emp in employees:
        print(f'  - {emp.first_name} {emp.last_name} ({emp.email}) - Role: {emp.role}')
    
    # Check employee role assignments
    print('\nEmployee role assignments:')
    emp_roles = EmployeeRole.query.limit(10).all()
    for er in emp_roles:
        employee = Employee.query.get(er.employee_id)
        role = Role.query.get(er.role_id)
        if employee and role:
            print(f'  - {employee.first_name} {employee.last_name} -> {role.name}')
    
    # Check super admin users
    print('\nAdmin users:')
    admin_employees = Employee.query.filter_by(role='admin').all()
    for admin in admin_employees:
        print(f'  - {admin.first_name} {admin.last_name} ({admin.email})')