from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.performance import PerformanceReview
from datetime import datetime

bp = Blueprint('performance', __name__, url_prefix='/api/performance')

@bp.route('', methods=['GET'])
@jwt_required()
def get_performance_reviews():
    """Get performance reviews"""
    employee_id = request.args.get('employee_id', None, type=int)
    status = request.args.get('status', None)
    
    query = PerformanceReview.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if status:
        query = query.filter_by(status=status)
    
    reviews = query.order_by(PerformanceReview.created_at.desc()).all()
    return jsonify([review.to_dict() for review in reviews]), 200

@bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_performance_review(review_id):
    """Get performance review by ID"""
    review = PerformanceReview.query.get_or_404(review_id)
    return jsonify(review.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_performance_review():
    """Create performance review"""
    reviewer_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['employee_id', 'review_period_start', 'review_period_end']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    review = PerformanceReview(
        employee_id=data['employee_id'],
        reviewer_id=reviewer_id,
        review_period_start=datetime.strptime(data['review_period_start'], '%Y-%m-%d').date(),
        review_period_end=datetime.strptime(data['review_period_end'], '%Y-%m-%d').date(),
        rating=data.get('rating'),
        goals_met=data.get('goals_met'),
        strengths=data.get('strengths'),
        areas_for_improvement=data.get('areas_for_improvement'),
        comments=data.get('comments'),
        status=data.get('status', 'draft')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201

@bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_performance_review(review_id):
    """Update performance review"""
    review = PerformanceReview.query.get_or_404(review_id)
    data = request.get_json()
    
    if 'rating' in data:
        review.rating = data['rating']
    if 'goals_met' in data:
        review.goals_met = data['goals_met']
    if 'strengths' in data:
        review.strengths = data['strengths']
    if 'areas_for_improvement' in data:
        review.areas_for_improvement = data['areas_for_improvement']
    if 'comments' in data:
        review.comments = data['comments']
    if 'status' in data:
        review.status = data['status']
    
    review.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(review.to_dict()), 200

@bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_performance_review(review_id):
    """Delete performance review"""
    review = PerformanceReview.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Performance review deleted successfully'}), 200
