from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.recruitment import JobPosting, Applicant
from datetime import datetime

bp = Blueprint('recruitment', __name__, url_prefix='/api/recruitment')

# Job Postings
@bp.route('/jobs', methods=['GET'])
def get_job_postings():
    """Get all job postings (public endpoint)"""
    status = request.args.get('status', 'open')
    jobs = JobPosting.query.filter_by(status=status).order_by(JobPosting.posted_date.desc()).all()
    return jsonify([job.to_dict() for job in jobs]), 200

@bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_posting(job_id):
    """Get job posting by ID (public endpoint)"""
    job = JobPosting.query.get_or_404(job_id)
    return jsonify(job.to_dict()), 200

@bp.route('/jobs', methods=['POST'])
@jwt_required()
def create_job_posting():
    """Create job posting"""
    data = request.get_json()
    
    required_fields = ['title', 'description', 'posted_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    job = JobPosting(
        title=data['title'],
        description=data['description'],
        department_id=data.get('department_id'),
        requirements=data.get('requirements'),
        salary_range=data.get('salary_range'),
        location=data.get('location'),
        employment_type=data.get('employment_type'),
        status=data.get('status', 'open'),
        posted_by=data.get('posted_by'),
        posted_date=datetime.strptime(data['posted_date'], '%Y-%m-%d').date(),
        closing_date=datetime.strptime(data['closing_date'], '%Y-%m-%d').date() if data.get('closing_date') else None
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify(job.to_dict()), 201

@bp.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job_posting(job_id):
    """Update job posting"""
    job = JobPosting.query.get_or_404(job_id)
    data = request.get_json()
    
    if 'title' in data:
        job.title = data['title']
    if 'description' in data:
        job.description = data['description']
    if 'department_id' in data:
        job.department_id = data['department_id']
    if 'requirements' in data:
        job.requirements = data['requirements']
    if 'salary_range' in data:
        job.salary_range = data['salary_range']
    if 'location' in data:
        job.location = data['location']
    if 'employment_type' in data:
        job.employment_type = data['employment_type']
    if 'status' in data:
        job.status = data['status']
    if 'closing_date' in data:
        job.closing_date = datetime.strptime(data['closing_date'], '%Y-%m-%d').date()
    
    job.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(job.to_dict()), 200

@bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job_posting(job_id):
    """Delete job posting"""
    job = JobPosting.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job posting deleted successfully'}), 200

# Applicants
@bp.route('/applicants', methods=['GET'])
@jwt_required()
def get_applicants():
    """Get all applicants"""
    job_id = request.args.get('job_id', None, type=int)
    status = request.args.get('status', None)
    
    query = Applicant.query
    
    if job_id:
        query = query.filter_by(job_posting_id=job_id)
    if status:
        query = query.filter_by(status=status)
    
    applicants = query.order_by(Applicant.applied_date.desc()).all()
    return jsonify([applicant.to_dict() for applicant in applicants]), 200

@bp.route('/applicants/<int:applicant_id>', methods=['GET'])
@jwt_required()
def get_applicant(applicant_id):
    """Get applicant by ID"""
    applicant = Applicant.query.get_or_404(applicant_id)
    return jsonify(applicant.to_dict()), 200

@bp.route('/apply', methods=['POST'])
def apply_for_job():
    """Apply for a job (public endpoint)"""
    data = request.get_json()
    
    required_fields = ['job_posting_id', 'first_name', 'last_name', 'email', 'applied_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    applicant = Applicant(
        job_posting_id=data['job_posting_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone'),
        resume_url=data.get('resume_url'),
        cover_letter=data.get('cover_letter'),
        status='applied',
        applied_date=datetime.strptime(data['applied_date'], '%Y-%m-%d').date(),
        notes=data.get('notes')
    )
    
    db.session.add(applicant)
    db.session.commit()
    
    return jsonify(applicant.to_dict()), 201

@bp.route('/applicants/<int:applicant_id>', methods=['PUT'])
@jwt_required()
def update_applicant(applicant_id):
    """Update applicant status"""
    applicant = Applicant.query.get_or_404(applicant_id)
    data = request.get_json()
    
    if 'status' in data:
        applicant.status = data['status']
    if 'notes' in data:
        applicant.notes = data['notes']
    
    applicant.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(applicant.to_dict()), 200

@bp.route('/applicants/<int:applicant_id>', methods=['DELETE'])
@jwt_required()
def delete_applicant(applicant_id):
    """Delete applicant"""
    applicant = Applicant.query.get_or_404(applicant_id)
    db.session.delete(applicant)
    db.session.commit()
    return jsonify({'message': 'Applicant deleted successfully'}), 200
