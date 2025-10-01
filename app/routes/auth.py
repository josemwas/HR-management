from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """Authenticate employee and return JWT tokens"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    employee = Employee.query.filter_by(email=data['email']).first()
    
    if not employee or not employee.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if employee.status != 'active':
        return jsonify({'error': 'Account is not active'}), 403
    
    access_token = create_access_token(identity=employee.id)
    refresh_token = create_refresh_token(identity=employee.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'employee': employee.to_dict()
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_employee():
    """Get current authenticated employee"""
    employee_id = get_jwt_identity()
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict()), 200

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change employee password"""
    data = request.get_json()
    employee_id = get_jwt_identity()
    employee = Employee.query.get_or_404(employee_id)
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old and new passwords are required'}), 400
    
    if not employee.check_password(data['old_password']):
        return jsonify({'error': 'Invalid old password'}), 401
    
    employee.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200
