from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from app.models.department import Department
from datetime import datetime

bp = Blueprint('employees', __name__, url_prefix='/api/employees')

@bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', None)
    department_id = request.args.get('department_id', None, type=int)
    
    query = Employee.query
    
    if status:
        query = query.filter_by(status=status)
    if department_id:
        query = query.filter_by(department_id=department_id)
    
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
    """Get employee by ID"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_employee():
    """Create new employee"""
    data = request.get_json()
    
    required_fields = ['employee_id', 'email', 'first_name', 'last_name', 'hire_date', 'position']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if Employee.query.filter_by(employee_id=data['employee_id']).first():
        return jsonify({'error': 'Employee ID already exists'}), 400
    
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
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
    
    if data.get('password'):
        employee.set_password(data['password'])
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify(employee.to_dict()), 201

@bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update employee"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    
    if 'email' in data and data['email'] != employee.email:
        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        employee.email = data['email']
    
    if 'first_name' in data:
        employee.first_name = data['first_name']
    if 'last_name' in data:
        employee.last_name = data['last_name']
    if 'phone' in data:
        employee.phone = data['phone']
    if 'date_of_birth' in data:
        employee.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    if 'position' in data:
        employee.position = data['position']
    if 'department_id' in data:
        employee.department_id = data['department_id']
    if 'salary' in data:
        employee.salary = data['salary']
    if 'status' in data:
        employee.status = data['status']
    if 'address' in data:
        employee.address = data['address']
    if 'emergency_contact' in data:
        employee.emergency_contact = data['emergency_contact']
    if 'role' in data:
        employee.role = data['role']
    
    employee.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(employee.to_dict()), 200

@bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Delete employee"""
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'}), 200

@bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments"""
    departments = Department.query.all()
    return jsonify([dept.to_dict() for dept in departments]), 200

@bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    """Create new department"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Department name is required'}), 400
    
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Department name already exists'}), 400
    
    department = Department(
        name=data['name'],
        description=data.get('description'),
        manager_id=data.get('manager_id')
    )
    
    db.session.add(department)
    db.session.commit()
    
    return jsonify(department.to_dict()), 201
