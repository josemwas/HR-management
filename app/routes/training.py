from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.training import TrainingProgram, TrainingEnrollment, EmployeeDocument, EmployeeBenefit
from app.models.employee import Employee
from app import db
from datetime import datetime
import os

bp = Blueprint('training', __name__, url_prefix='/api/training')

# Training Programs endpoints
@bp.route('/programs', methods=['GET'])
@jwt_required()
def get_training_programs():
    """Get all training programs"""
    try:
        programs = TrainingProgram.query.all()
        return jsonify([program.to_dict() for program in programs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/programs', methods=['POST'])
@jwt_required()
def create_training_program():
    """Create a new training program"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        program = TrainingProgram(
            title=data['title'],
            description=data.get('description'),
            trainer=data.get('trainer'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            duration_hours=data.get('duration_hours'),
            max_participants=data.get('max_participants', 20),
            location=data.get('location'),
            training_type=data.get('training_type', 'internal'),
            status=data.get('status', 'scheduled')
        )
        
        db.session.add(program)
        db.session.commit()
        
        return jsonify(program.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/programs/<int:program_id>', methods=['PUT'])
@jwt_required()
def update_training_program(program_id):
    """Update a training program"""
    try:
        program = TrainingProgram.query.get_or_404(program_id)
        data = request.json
        
        # Update fields
        if 'title' in data:
            program.title = data['title']
        if 'description' in data:
            program.description = data['description']
        if 'trainer' in data:
            program.trainer = data['trainer']
        if 'start_date' in data:
            program.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            program.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        if 'duration_hours' in data:
            program.duration_hours = data['duration_hours']
        if 'max_participants' in data:
            program.max_participants = data['max_participants']
        if 'location' in data:
            program.location = data['location']
        if 'training_type' in data:
            program.training_type = data['training_type']
        if 'status' in data:
            program.status = data['status']
        
        program.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(program.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def delete_training_program(program_id):
    """Delete a training program"""
    try:
        program = TrainingProgram.query.get_or_404(program_id)
        db.session.delete(program)
        db.session.commit()
        
        return jsonify({'message': 'Training program deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Training Enrollments endpoints
@bp.route('/enrollments', methods=['GET'])
@jwt_required()
def get_training_enrollments():
    """Get all training enrollments"""
    try:
        enrollments = TrainingEnrollment.query.all()
        return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enrollments', methods=['POST'])
@jwt_required()
def create_training_enrollment():
    """Enroll employee in training program"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['employee_id', 'program_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if enrollment already exists
        existing_enrollment = TrainingEnrollment.query.filter_by(
            employee_id=data['employee_id'],
            program_id=data['program_id']
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Employee already enrolled in this program'}), 400
        
        # Check program capacity
        program = TrainingProgram.query.get_or_404(data['program_id'])
        current_enrollments = len(program.enrollments)
        if current_enrollments >= program.max_participants:
            return jsonify({'error': 'Training program is at full capacity'}), 400
        
        enrollment = TrainingEnrollment(
            employee_id=data['employee_id'],
            program_id=data['program_id'],
            completion_status=data.get('completion_status', 'enrolled')
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify(enrollment.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enrollments/<int:enrollment_id>/complete', methods=['PUT'])
@jwt_required()
def complete_training(enrollment_id):
    """Mark training as completed"""
    try:
        enrollment = TrainingEnrollment.query.get_or_404(enrollment_id)
        data = request.json
        
        enrollment.completion_status = 'completed'
        enrollment.completion_date = datetime.utcnow()
        enrollment.score = data.get('score')
        enrollment.feedback = data.get('feedback')
        enrollment.certificate_issued = data.get('certificate_issued', False)
        enrollment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(enrollment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Document Management endpoints
@bp.route('/documents', methods=['GET'])
@jwt_required()
def get_employee_documents():
    """Get employee documents"""
    try:
        employee_id = request.args.get('employee_id')
        if employee_id:
            documents = EmployeeDocument.query.filter_by(employee_id=employee_id).all()
        else:
            documents = EmployeeDocument.query.all()
        
        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/documents', methods=['POST'])
@jwt_required()
def upload_employee_document():
    """Upload employee document (simplified - would need file handling in production)"""
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['employee_id', 'document_name', 'document_type', 'file_path']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        document = EmployeeDocument(
            employee_id=data['employee_id'],
            document_name=data['document_name'],
            document_type=data['document_type'],
            file_path=data['file_path'],
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type'),
            uploaded_by=current_user_id,
            is_confidential=data.get('is_confidential', False),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            notes=data.get('notes')
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify(document.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_employee_document(document_id):
    """Delete employee document"""
    try:
        document = EmployeeDocument.query.get_or_404(document_id)
        
        # In production, also delete the actual file
        # os.remove(document.file_path)
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Benefits Management endpoints
@bp.route('/benefits', methods=['GET'])
@jwt_required()
def get_employee_benefits():
    """Get employee benefits"""
    try:
        employee_id = request.args.get('employee_id')
        if employee_id:
            benefits = EmployeeBenefit.query.filter_by(employee_id=employee_id).all()
        else:
            benefits = EmployeeBenefit.query.all()
        
        return jsonify([benefit.to_dict() for benefit in benefits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/benefits', methods=['POST'])
@jwt_required()
def create_employee_benefit():
    """Create employee benefit"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['employee_id', 'benefit_type', 'benefit_name', 'start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        benefit = EmployeeBenefit(
            employee_id=data['employee_id'],
            benefit_type=data['benefit_type'],
            benefit_name=data['benefit_name'],
            provider=data.get('provider'),
            policy_number=data.get('policy_number'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            premium_amount=data.get('premium_amount'),
            employer_contribution=data.get('employer_contribution'),
            employee_contribution=data.get('employee_contribution'),
            coverage_details=data.get('coverage_details'),
            status=data.get('status', 'active')
        )
        
        db.session.add(benefit)
        db.session.commit()
        
        return jsonify(benefit.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/benefits/<int:benefit_id>', methods=['PUT'])
@jwt_required()
def update_employee_benefit(benefit_id):
    """Update employee benefit"""
    try:
        benefit = EmployeeBenefit.query.get_or_404(benefit_id)
        data = request.json
        
        # Update fields
        for field in ['benefit_type', 'benefit_name', 'provider', 'policy_number', 
                      'premium_amount', 'employer_contribution', 'employee_contribution', 
                      'coverage_details', 'status']:
            if field in data:
                setattr(benefit, field, data[field])
        
        if 'start_date' in data:
            benefit.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            benefit.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        
        benefit.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(benefit.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/benefits/<int:benefit_id>', methods=['DELETE'])
@jwt_required()
def delete_employee_benefit(benefit_id):
    """Delete employee benefit"""
    try:
        benefit = EmployeeBenefit.query.get_or_404(benefit_id)
        db.session.delete(benefit)
        db.session.commit()
        
        return jsonify({'message': 'Benefit deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500