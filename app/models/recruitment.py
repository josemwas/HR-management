from datetime import datetime
from app import db

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract
    status = db.Column(db.String(20), default='open')  # open, closed, filled
    posted_by = db.Column(db.Integer)
    posted_date = db.Column(db.Date, nullable=False)
    closing_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applicants = db.relationship('Applicant', back_populates='job_posting', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'department_id': self.department_id,
            'requirements': self.requirements,
            'salary_range': self.salary_range,
            'location': self.location,
            'employment_type': self.employment_type,
            'status': self.status,
            'posted_by': self.posted_by,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Applicant(db.Model):
    __tablename__ = 'applicants'
    
    id = db.Column(db.Integer, primary_key=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    resume_url = db.Column(db.String(500))
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='applied')  # applied, screening, interview, offered, rejected, hired
    applied_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_posting = db.relationship('JobPosting', back_populates='applicants')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'resume_url': self.resume_url,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
