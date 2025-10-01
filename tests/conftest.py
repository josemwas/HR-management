import pytest
from app import create_app, db
from app.models import Employee, Department
from datetime import date

@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_department(app):
    """Create a sample department"""
    with app.app_context():
        dept = Department(name='IT', description='Information Technology')
        db.session.add(dept)
        db.session.commit()
        dept_id = dept.id
        db.session.refresh(dept)
    return dept_id

@pytest.fixture
def sample_employee(app, sample_department):
    """Create a sample employee"""
    with app.app_context():
        employee = Employee(
            employee_id='EMP001',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            hire_date=date.today(),
            position='Software Engineer',
            department_id=sample_department,
            salary=75000,
            role='employee',
            status='active'
        )
        employee.set_password('password123')
        db.session.add(employee)
        db.session.commit()
        emp_id = employee.id
        db.session.refresh(employee)
    return emp_id

@pytest.fixture
def auth_headers(client, sample_employee):
    """Get authentication headers with JWT token"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    data = response.get_json()
    return {'Authorization': f"Bearer {data['access_token']}"}
