from datetime import datetime
from app import db

class PerformanceReview(db.Model):
    __tablename__ = 'performance_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Float)  # 0-5 scale
    goals_met = db.Column(db.Text)
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, acknowledged
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='performance_reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'reviewer_id': self.reviewer_id,
            'review_period_start': self.review_period_start.isoformat() if self.review_period_start else None,
            'review_period_end': self.review_period_end.isoformat() if self.review_period_end else None,
            'rating': self.rating,
            'goals_met': self.goals_met,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'comments': self.comments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
