from datetime import datetime
from app import db

class TrainingProgram(db.Model):
    """Training Program model for employee development"""
    __tablename__ = 'training_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    trainer = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    duration_hours = db.Column(db.Integer)  # Training duration in hours
    max_participants = db.Column(db.Integer, default=20)
    location = db.Column(db.String(200))
    training_type = db.Column(db.String(50), default='internal')  # internal, external, online
    status = db.Column(db.String(20), default='scheduled')  # scheduled, ongoing, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('TrainingEnrollment', backref='program', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'trainer': self.trainer,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_hours': self.duration_hours,
            'max_participants': self.max_participants,
            'current_participants': len(self.enrollments),
            'location': self.location,
            'training_type': self.training_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TrainingEnrollment(db.Model):
    """Training Enrollment model to track employee participation"""
    __tablename__ = 'training_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('training_programs.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_status = db.Column(db.String(20), default='enrolled')  # enrolled, in_progress, completed, dropped
    completion_date = db.Column(db.DateTime)
    score = db.Column(db.Float)  # Training assessment score (0-100)
    feedback = db.Column(db.Text)
    certificate_issued = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollment_employee = db.relationship('Employee', foreign_keys=[employee_id], backref='training_enrollments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.enrollment_employee.first_name} {self.enrollment_employee.last_name}" if hasattr(self, 'enrollment_employee') and self.enrollment_employee else None,
            'program_id': self.program_id,
            'program_title': self.program.title if hasattr(self, 'program') and self.program else None,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'completion_status': self.completion_status,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'score': self.score,
            'feedback': self.feedback,
            'certificate_issued': self.certificate_issued
        }

class EmployeeDocument(db.Model):
    """Employee Document model for document management"""
    __tablename__ = 'employee_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    document_name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # resume, contract, id_copy, etc.
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_confidential = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date)  # For documents like ID cards, contracts
    notes = db.Column(db.Text)
    
    # Relationships
    document_employee = db.relationship('Employee', foreign_keys=[employee_id], backref='documents')
    uploader = db.relationship('Employee', foreign_keys=[uploaded_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.document_employee.first_name} {self.document_employee.last_name}" if hasattr(self, 'document_employee') and self.document_employee else None,
            'document_name': self.document_name,
            'document_type': self.document_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_confidential': self.is_confidential,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notes': self.notes
        }

class EmployeeBenefit(db.Model):
    """Employee Benefits model for benefits management"""
    __tablename__ = 'employee_benefits'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    benefit_type = db.Column(db.String(50), nullable=False)  # health, dental, life_insurance, retirement, etc.
    benefit_name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100))
    policy_number = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    premium_amount = db.Column(db.Numeric(10, 2))
    employer_contribution = db.Column(db.Numeric(10, 2))
    employee_contribution = db.Column(db.Numeric(10, 2))
    coverage_details = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, suspended, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    benefit_employee = db.relationship('Employee', foreign_keys=[employee_id], backref='benefits')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.benefit_employee.first_name} {self.benefit_employee.last_name}" if hasattr(self, 'benefit_employee') and self.benefit_employee else None,
            'benefit_type': self.benefit_type,
            'benefit_name': self.benefit_name,
            'provider': self.provider,
            'policy_number': self.policy_number,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'premium_amount': float(self.premium_amount) if self.premium_amount else None,
            'employer_contribution': float(self.employer_contribution) if self.employer_contribution else None,
            'employee_contribution': float(self.employee_contribution) if self.employee_contribution else None,
            'coverage_details': self.coverage_details,
            'status': self.status
        }