from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from app.models.training import EmployeeBenefit
from datetime import datetime

bp = Blueprint('benefits', __name__, url_prefix='/api/benefits')

@bp.route('', methods=['GET'])
@jwt_required()
def get_benefits():
    """Get all benefit packages"""
    try:
        benefits = EmployeeBenefit.query.all()
        return jsonify([benefit.to_dict() for benefit in benefits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
@jwt_required()
def create_benefit():
    """Create a new benefit package"""
    try:
        data = request.json
        
        benefit = EmployeeBenefit(
            employee_id=data.get('employee_id'),
            benefit_type=data.get('benefit_type'),
            description=data.get('description'),
            value=data.get('value'),
            effective_date=datetime.strptime(data.get('effective_date'), '%Y-%m-%d') if data.get('effective_date') else None,
            expiry_date=datetime.strptime(data.get('expiry_date'), '%Y-%m-%d') if data.get('expiry_date') else None,
            status=data.get('status', 'active')
        )
        
        db.session.add(benefit)
        db.session.commit()
        
        return jsonify(benefit.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:benefit_id>', methods=['GET'])
@jwt_required()
def get_benefit(benefit_id):
    """Get specific benefit package"""
    try:
        benefit = EmployeeBenefit.query.get_or_404(benefit_id)
        return jsonify(benefit.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:benefit_id>', methods=['PUT'])
@jwt_required()
def update_benefit(benefit_id):
    """Update benefit package"""
    try:
        benefit = EmployeeBenefit.query.get_or_404(benefit_id)
        data = request.json
        
        benefit.benefit_type = data.get('benefit_type', benefit.benefit_type)
        benefit.description = data.get('description', benefit.description)
        benefit.value = data.get('value', benefit.value)
        benefit.status = data.get('status', benefit.status)
        
        if data.get('effective_date'):
            benefit.effective_date = datetime.strptime(data.get('effective_date'), '%Y-%m-%d')
        if data.get('expiry_date'):
            benefit.expiry_date = datetime.strptime(data.get('expiry_date'), '%Y-%m-%d')
        
        benefit.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(benefit.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:benefit_id>', methods=['DELETE'])
@jwt_required()
def delete_benefit(benefit_id):
    """Delete benefit package"""
    try:
        benefit = EmployeeBenefit.query.get_or_404(benefit_id)
        db.session.delete(benefit)
        db.session.commit()
        
        return jsonify({'message': 'Benefit package deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/employee/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee_benefits(employee_id):
    """Get benefits for specific employee"""
    try:
        benefits = EmployeeBenefit.query.filter_by(employee_id=employee_id).all()
        return jsonify([benefit.to_dict() for benefit in benefits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_employee():
    """Enroll employee in benefit package"""
    try:
        data = request.json
        
        # Check if enrollment already exists
        existing = EmployeeBenefit.query.filter_by(
            employee_id=data.get('employee_id'),
            benefit_type=data.get('benefit_type')
        ).first()
        
        if existing:
            return jsonify({'error': 'Employee already enrolled in this benefit'}), 400
        
        benefit = EmployeeBenefit(
            employee_id=data.get('employee_id'),
            benefit_type=data.get('benefit_type'),
            description=data.get('description'),
            value=data.get('value'),
            effective_date=datetime.strptime(data.get('effective_date'), '%Y-%m-%d'),
            status='active'
        )
        
        db.session.add(benefit)
        db.session.commit()
        
        return jsonify(benefit.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_benefits_stats():
    """Get benefits statistics"""
    try:
        total_packages = EmployeeBenefit.query.count()
        active_enrollments = EmployeeBenefit.query.filter_by(status='active').count()
        
        # Calculate monthly cost (simplified)
        total_cost = db.session.query(db.func.sum(EmployeeBenefit.value)).scalar() or 0
        
        stats = {
            'total_packages': total_packages,
            'active_enrollments': active_enrollments,
            'pending_reviews': 7,  # Mock data
            'monthly_cost': float(total_cost)
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500