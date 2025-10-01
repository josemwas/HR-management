from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.payroll import Payroll
from datetime import datetime

bp = Blueprint('payroll', __name__, url_prefix='/api/payroll')

@bp.route('', methods=['GET'])
@jwt_required()
def get_payrolls():
    """Get payroll records"""
    employee_id = request.args.get('employee_id', None, type=int)
    month = request.args.get('month', None, type=int)
    year = request.args.get('year', None, type=int)
    status = request.args.get('status', None)
    
    query = Payroll.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
    if status:
        query = query.filter_by(status=status)
    
    payrolls = query.order_by(Payroll.year.desc(), Payroll.month.desc()).all()
    return jsonify([payroll.to_dict() for payroll in payrolls]), 200

@bp.route('/<int:payroll_id>', methods=['GET'])
@jwt_required()
def get_payroll(payroll_id):
    """Get payroll by ID"""
    payroll = Payroll.query.get_or_404(payroll_id)
    return jsonify(payroll.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_payroll():
    """Create payroll record"""
    data = request.get_json()
    
    required_fields = ['employee_id', 'month', 'year', 'basic_salary', 'net_salary']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if payroll already exists for employee in that month/year
    existing = Payroll.query.filter_by(
        employee_id=data['employee_id'],
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'error': 'Payroll already exists for this employee in this month/year'}), 400
    
    payroll = Payroll(
        employee_id=data['employee_id'],
        month=data['month'],
        year=data['year'],
        basic_salary=data['basic_salary'],
        allowances=data.get('allowances', 0.0),
        deductions=data.get('deductions', 0.0),
        bonus=data.get('bonus', 0.0),
        net_salary=data['net_salary'],
        payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else None,
        payment_method=data.get('payment_method'),
        status=data.get('status', 'pending'),
        notes=data.get('notes')
    )
    
    db.session.add(payroll)
    db.session.commit()
    
    return jsonify(payroll.to_dict()), 201

@bp.route('/<int:payroll_id>', methods=['PUT'])
@jwt_required()
def update_payroll(payroll_id):
    """Update payroll record"""
    payroll = Payroll.query.get_or_404(payroll_id)
    data = request.get_json()
    
    if 'basic_salary' in data:
        payroll.basic_salary = data['basic_salary']
    if 'allowances' in data:
        payroll.allowances = data['allowances']
    if 'deductions' in data:
        payroll.deductions = data['deductions']
    if 'bonus' in data:
        payroll.bonus = data['bonus']
    if 'net_salary' in data:
        payroll.net_salary = data['net_salary']
    if 'payment_date' in data:
        payroll.payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
    if 'payment_method' in data:
        payroll.payment_method = data['payment_method']
    if 'status' in data:
        payroll.status = data['status']
    if 'notes' in data:
        payroll.notes = data['notes']
    
    payroll.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(payroll.to_dict()), 200

@bp.route('/<int:payroll_id>', methods=['DELETE'])
@jwt_required()
def delete_payroll(payroll_id):
    """Delete payroll record"""
    payroll = Payroll.query.get_or_404(payroll_id)
    db.session.delete(payroll)
    db.session.commit()
    return jsonify({'message': 'Payroll record deleted successfully'}), 200
