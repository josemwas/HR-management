from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.leave import Leave
from datetime import datetime

bp = Blueprint('leaves', __name__, url_prefix='/api/leaves')

@bp.route('', methods=['GET'])
@jwt_required()
def get_leaves():
    """Get leave records"""
    employee_id = request.args.get('employee_id', None, type=int)
    status = request.args.get('status', None)
    
    query = Leave.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if status:
        query = query.filter_by(status=status)
    
    leaves = query.order_by(Leave.created_at.desc()).all()
    return jsonify([leave.to_dict() for leave in leaves]), 200

@bp.route('/<int:leave_id>', methods=['GET'])
@jwt_required()
def get_leave(leave_id):
    """Get leave by ID"""
    leave = Leave.query.get_or_404(leave_id)
    return jsonify(leave.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_leave():
    """Create leave request"""
    employee_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['leave_type', 'start_date', 'end_date', 'days']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    leave = Leave(
        employee_id=employee_id,
        leave_type=data['leave_type'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        days=data['days'],
        reason=data.get('reason'),
        status='pending'
    )
    
    db.session.add(leave)
    db.session.commit()
    
    return jsonify(leave.to_dict()), 201

@bp.route('/<int:leave_id>/approve', methods=['POST'])
@jwt_required()
def approve_leave(leave_id):
    """Approve leave request"""
    leave = Leave.query.get_or_404(leave_id)
    approver_id = get_jwt_identity()
    
    if leave.status != 'pending':
        return jsonify({'error': 'Leave request is not pending'}), 400
    
    leave.status = 'approved'
    leave.approved_by = approver_id
    leave.approved_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(leave.to_dict()), 200

@bp.route('/<int:leave_id>/reject', methods=['POST'])
@jwt_required()
def reject_leave(leave_id):
    """Reject leave request"""
    leave = Leave.query.get_or_404(leave_id)
    approver_id = get_jwt_identity()
    
    if leave.status != 'pending':
        return jsonify({'error': 'Leave request is not pending'}), 400
    
    leave.status = 'rejected'
    leave.approved_by = approver_id
    leave.approved_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(leave.to_dict()), 200

@bp.route('/<int:leave_id>', methods=['PUT'])
@jwt_required()
def update_leave(leave_id):
    """Update leave request"""
    leave = Leave.query.get_or_404(leave_id)
    data = request.get_json()
    
    if leave.status != 'pending':
        return jsonify({'error': 'Cannot update approved or rejected leave'}), 400
    
    if 'leave_type' in data:
        leave.leave_type = data['leave_type']
    if 'start_date' in data:
        leave.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        leave.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if 'days' in data:
        leave.days = data['days']
    if 'reason' in data:
        leave.reason = data['reason']
    
    leave.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(leave.to_dict()), 200

@bp.route('/<int:leave_id>', methods=['DELETE'])
@jwt_required()
def delete_leave(leave_id):
    """Delete leave request"""
    leave = Leave.query.get_or_404(leave_id)
    
    if leave.status != 'pending':
        return jsonify({'error': 'Cannot delete approved or rejected leave'}), 400
    
    db.session.delete(leave)
    db.session.commit()
    return jsonify({'message': 'Leave request deleted successfully'}), 200
