from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.attendance import Attendance
from datetime import datetime, date

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@bp.route('', methods=['GET'])
@jwt_required()
def get_attendances():
    """Get attendance records"""
    employee_id = request.args.get('employee_id', None, type=int)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    query = Attendance.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if start_date:
        query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    attendances = query.order_by(Attendance.date.desc()).all()
    return jsonify([att.to_dict() for att in attendances]), 200

@bp.route('/<int:attendance_id>', methods=['GET'])
@jwt_required()
def get_attendance(attendance_id):
    """Get attendance by ID"""
    attendance = Attendance.query.get_or_404(attendance_id)
    return jsonify(attendance.to_dict()), 200

@bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    """Check in for the day"""
    employee_id = get_jwt_identity()
    today = date.today()
    
    existing = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if existing:
        return jsonify({'error': 'Already checked in for today'}), 400
    
    attendance = Attendance(
        employee_id=employee_id,
        date=today,
        check_in=datetime.utcnow(),
        status='present'
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 201

@bp.route('/check-out', methods=['POST'])
@jwt_required()
def check_out():
    """Check out for the day"""
    employee_id = get_jwt_identity()
    today = date.today()
    
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if not attendance:
        return jsonify({'error': 'No check-in record found for today'}), 400
    
    if attendance.check_out:
        return jsonify({'error': 'Already checked out for today'}), 400
    
    attendance.check_out = datetime.utcnow()
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_attendance():
    """Create attendance record (for admins)"""
    data = request.get_json()
    
    if not data or not data.get('employee_id') or not data.get('date'):
        return jsonify({'error': 'Employee ID and date are required'}), 400
    
    attendance = Attendance(
        employee_id=data['employee_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        check_in=datetime.strptime(data['check_in'], '%Y-%m-%d %H:%M:%S') if data.get('check_in') else None,
        check_out=datetime.strptime(data['check_out'], '%Y-%m-%d %H:%M:%S') if data.get('check_out') else None,
        status=data.get('status', 'present'),
        notes=data.get('notes')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 201

@bp.route('/<int:attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance(attendance_id):
    """Update attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    data = request.get_json()
    
    if 'check_in' in data:
        attendance.check_in = datetime.strptime(data['check_in'], '%Y-%m-%d %H:%M:%S')
    if 'check_out' in data:
        attendance.check_out = datetime.strptime(data['check_out'], '%Y-%m-%d %H:%M:%S')
    if 'status' in data:
        attendance.status = data['status']
    if 'notes' in data:
        attendance.notes = data['notes']
    
    db.session.commit()
    return jsonify(attendance.to_dict()), 200

@bp.route('/<int:attendance_id>', methods=['DELETE'])
@jwt_required()
def delete_attendance(attendance_id):
    """Delete attendance record"""
    attendance = Attendance.query.get_or_404(attendance_id)
    db.session.delete(attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance record deleted successfully'}), 200
