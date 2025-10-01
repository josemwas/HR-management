import pytest
from datetime import date

def test_get_employees(client, auth_headers, sample_employee):
    """Test getting all employees"""
    response = client.get('/api/employees', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'employees' in data
    assert len(data['employees']) > 0

def test_get_employee_by_id(client, auth_headers, sample_employee):
    """Test getting employee by ID"""
    response = client.get(f'/api/employees/{sample_employee}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'test@example.com'

def test_create_employee(client, auth_headers, sample_department):
    """Test creating a new employee"""
    response = client.post('/api/employees',
                          headers=auth_headers,
                          json={
                              'employee_id': 'EMP002',
                              'email': 'newemployee@example.com',
                              'first_name': 'Jane',
                              'last_name': 'Smith',
                              'hire_date': '2024-01-01',
                              'position': 'Manager',
                              'department_id': sample_department,
                              'salary': 85000,
                              'password': 'password123'
                          })
    assert response.status_code == 201
    data = response.get_json()
    assert data['email'] == 'newemployee@example.com'

def test_create_employee_duplicate_email(client, auth_headers, sample_employee, sample_department):
    """Test creating employee with duplicate email"""
    response = client.post('/api/employees',
                          headers=auth_headers,
                          json={
                              'employee_id': 'EMP003',
                              'email': 'test@example.com',
                              'first_name': 'Jane',
                              'last_name': 'Smith',
                              'hire_date': '2024-01-01',
                              'position': 'Manager',
                              'department_id': sample_department
                          })
    assert response.status_code == 400

def test_update_employee(client, auth_headers, sample_employee):
    """Test updating employee"""
    response = client.put(f'/api/employees/{sample_employee}',
                         headers=auth_headers,
                         json={
                             'position': 'Senior Software Engineer',
                             'salary': 90000
                         })
    assert response.status_code == 200
    data = response.get_json()
    assert data['position'] == 'Senior Software Engineer'
    assert data['salary'] == 90000

def test_delete_employee(client, auth_headers, sample_employee):
    """Test deleting employee"""
    response = client.delete(f'/api/employees/{sample_employee}', headers=auth_headers)
    assert response.status_code == 200

def test_get_departments(client, auth_headers, sample_department):
    """Test getting all departments"""
    response = client.get('/api/employees/departments', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[0]['name'] == 'IT'

def test_create_department(client, auth_headers):
    """Test creating a new department"""
    response = client.post('/api/employees/departments',
                          headers=auth_headers,
                          json={
                              'name': 'HR',
                              'description': 'Human Resources'
                          })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'HR'
