from app import create_app
from app.models.employee import Employee

app = create_app()
with app.app_context():
    # List all employees with their credentials
    employees = Employee.query.all()
    print("Available users for testing:")
    print("=" * 50)
    
    for emp in employees:
        print(f"Name: {emp.first_name} {emp.last_name}")
        print(f"Email: {emp.email}")
        print(f"Role: {emp.role}")
        print(f"Organization: {emp.organization.name if emp.organization else 'None'}")
        print(f"Password hint: Check init_sample_data.py or init_saas_sample_data.py")
        print("-" * 30)
    
    print("\nDefault passwords are typically:")
    print("- admin123 (for admin users)")
    print("- password123 (for regular users)")
    print("- Or check the sample data initialization scripts")