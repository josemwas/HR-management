from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    hire_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    salary = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(200))
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='employees')
    attendances = db.relationship('Attendance', back_populates='employee', cascade='all, delete-orphan')
    leaves = db.relationship('Leave', back_populates='employee', cascade='all, delete-orphan')
    payrolls = db.relationship('Payroll', back_populates='employee', cascade='all, delete-orphan')
    performance_reviews = db.relationship('PerformanceReview', back_populates='employee', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'position': self.position,
            'department_id': self.department_id,
            'salary': self.salary,
            'status': self.status,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
