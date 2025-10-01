from datetime import datetime
from app import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add unique constraint for department name within organization
    __table_args__ = (db.UniqueConstraint('organization_id', 'name', name='uq_org_dept_name'),)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='departments')
    employees = db.relationship('Employee', back_populates='department')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'employee_count': len(self.employees),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
