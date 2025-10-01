from datetime import datetime
from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)  # Nullable for system roles
    name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_system_role = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique role names within organization
    __table_args__ = (db.UniqueConstraint('organization_id', 'name', name='uq_org_role_name'),)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='roles')
    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles')
    employee_roles = db.relationship('EmployeeRole', back_populates='role', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'is_system_role': self.is_system_role,
            'is_active': self.is_active,
            'permissions': [p.to_dict() for p in self.permissions],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50), nullable=False)  # employees, attendance, leaves, etc.
    action = db.Column(db.String(50), nullable=False)  # create, read, update, delete, manage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'module': self.module,
            'action': self.action
        }

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique role-permission combinations
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)

class EmployeeRole(db.Model):
    __tablename__ = 'employee_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    is_primary = db.Column(db.Boolean, default=False)  # Primary role for the employee
    
    # Relationships
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='employee_roles')
    role = db.relationship('Role', back_populates='employee_roles')
    assigner = db.relationship('Employee', foreign_keys=[assigned_by])
    
    # Ensure unique employee-role combinations
    __table_args__ = (db.UniqueConstraint('employee_id', 'role_id', name='uq_employee_role'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'role_id': self.role_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'is_primary': self.is_primary,
            'role': self.role.to_dict() if self.role else None
        }

class OrganizationSetting(db.Model):
    __tablename__ = 'organization_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # general, attendance, leaves, payroll, etc.
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.Text)
    is_sensitive = db.Column(db.Boolean, default=False)  # For passwords, API keys, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique setting keys within organization
    __table_args__ = (db.UniqueConstraint('organization_id', 'key', name='uq_org_setting_key'),)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='settings')
    
    def get_value(self):
        """Return the value in the appropriate data type."""
        if self.data_type == 'boolean':
            return self.value.lower() == 'true'
        elif self.data_type == 'integer':
            return int(self.value) if self.value else 0
        elif self.data_type == 'json':
            import json
            return json.loads(self.value) if self.value else {}
        else:
            return self.value
    
    def set_value(self, value):
        """Set the value with appropriate conversion."""
        if self.data_type == 'boolean':
            self.value = str(bool(value)).lower()
        elif self.data_type == 'integer':
            self.value = str(int(value))
        elif self.data_type == 'json':
            import json
            self.value = json.dumps(value)
        else:
            self.value = str(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'category': self.category,
            'key': self.key,
            'value': self.get_value() if not self.is_sensitive else '***',
            'data_type': self.data_type,
            'description': self.description,
            'is_sensitive': self.is_sensitive,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # employee, role, setting, etc.
    resource_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON string of old values
    new_values = db.Column(db.Text)  # JSON string of new values
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    organization = db.relationship('Organization')
    user = db.relationship('Employee')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user': {
                'id': self.user.id,
                'name': f"{self.user.first_name} {self.user.last_name}",
                'email': self.user.email
            } if self.user else None
        }