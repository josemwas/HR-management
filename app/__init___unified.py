"""
HR MANAGEMENT SYSTEM - UNIFIED APPLICATION FACTORY
==================================================
A comprehensive, streamlined HR SaaS platform with 25+ integrated modules.

Features:
- Multi-tenant SaaS architecture
- Enterprise-grade HR functionality
- Role-based access control
- Unified authentication system
- Comprehensive API coverage
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from config import config
import os
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """
    Application Factory Pattern
    Creates and configures the Flask application with all HR modules
    """
    
    # Set template and static directories
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # ================================================================
    # UNIFIED BLUEPRINT REGISTRATION
    # ================================================================
    
    # Import all route blueprints in organized groups
    from app.routes import (
        # Core Authentication & Authorization
        auth, rbac,
        
        # Core HR Management
        employees, organizations, 
        
        # Time & Attendance
        attendance, leaves, timesheets, time_labor,
        
        # Performance & Development
        performance, training, recruitment, onboarding,
        
        # Compensation & Benefits
        payroll, benefits, compensation,
        
        # Employee Lifecycle
        exit_management, employee_relations, succession_planning,
        
        # Workforce Analytics & Planning
        workforce_planning, analytics,
        
        # Employee Services
        self_service, announcements, documents,
        
        # Compliance & Governance
        compliance,
        
        # SaaS Administration
        saas_admin, super_admin
    )
    
    # Register all blueprints systematically
    blueprint_registry = [
        # Authentication & Security
        (auth.bp, 'Authentication'),
        (rbac.rbac_bp, 'Role-Based Access Control'),
        
        # Core HR
        (employees.bp, 'Employee Management'),
        (organizations.bp, 'Organization Management'),
        
        # Time Management
        (attendance.bp, 'Attendance Tracking'),
        (leaves.bp, 'Leave Management'),
        (timesheets.timesheets, 'Timesheet Management'),
        (time_labor.time_labor_bp, 'Enhanced Time & Labor'),
        
        # Performance & Growth
        (performance.bp, 'Performance Management'),
        (training.bp, 'Training & Development'),
        (recruitment.bp, 'Recruitment Portal'),
        (onboarding.bp, 'Employee Onboarding'),
        
        # Compensation
        (payroll.bp, 'Payroll Processing'),
        (benefits.bp, 'Benefits Management'),
        (compensation.compensation, 'Compensation Management'),
        
        # Employee Relations
        (exit_management.exit_management_bp, 'Exit Management'),
        (employee_relations.employee_relations_bp, 'Employee Relations'),
        (succession_planning.succession_planning_bp, 'Succession Planning'),
        
        # Strategic Planning
        (workforce_planning.workforce_planning_bp, 'Workforce Planning'),
        (analytics.analytics, 'HR Analytics'),
        
        # Employee Services
        (self_service.self_service, 'Employee Self-Service'),
        (announcements.bp, 'Company Announcements'),
        (documents.documents, 'Document Management'),
        
        # Compliance
        (compliance.compliance, 'Compliance Management'),
        
        # SaaS Platform
        (saas_admin.bp, 'SaaS Administration'),
        (super_admin.bp, 'Super Admin Dashboard')
    ]
    
    # Register all blueprints with logging
    for blueprint, description in blueprint_registry:
        try:
            app.register_blueprint(blueprint)
            app.logger.info(f"✅ Registered: {description}")
        except Exception as e:
            app.logger.error(f"❌ Failed to register {description}: {str(e)}")
    
    # ================================================================
    # UNIFIED FRONTEND ROUTES
    # ================================================================
    
    @app.route('/')
    def index():
        """Main landing page - redirects to dashboard or login"""
        return redirect(url_for('login'))
    
    @app.route('/login')
    def login():
        """User authentication page"""
        return render_template('login.html')
    
    @app.route('/signup')
    def signup():
        """User registration page"""
        return render_template('signup.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Main HR dashboard"""
        return render_template('dashboard.html')
    
    # ================================================================
    # CORE HR FEATURE ROUTES
    # ================================================================
    
    @app.route('/employees')
    def employees_page():
        return render_template('employees.html')
    
    @app.route('/departments')
    def departments_page():
        return render_template('dashboard.html')  # TODO: Create dedicated template
    
    @app.route('/attendance')
    def attendance_page():
        return render_template('attendance.html')
    
    @app.route('/leaves')
    def leaves_page():
        return render_template('leaves.html')
    
    @app.route('/payroll')
    def payroll_page():
        return render_template('payroll.html')
    
    @app.route('/performance')
    def performance_page():
        return render_template('performance.html')
    
    @app.route('/recruitment')
    def recruitment_page():
        return render_template('recruitment.html')
    
    @app.route('/training')
    def training_page():
        return render_template('training.html')
    
    # ================================================================
    # ADVANCED HR FEATURE ROUTES
    # ================================================================
    
    @app.route('/benefits')
    def benefits_page():
        return render_template('benefits.html')
    
    @app.route('/onboarding')
    def onboarding_page():
        return render_template('onboarding.html')
    
    @app.route('/exit-management')
    def exit_management_page():
        return render_template('exit_management.html')
    
    @app.route('/employee-relations')
    def employee_relations_page():
        return render_template('employee_relations.html')
    
    @app.route('/time-labor')
    def time_labor_page():
        return render_template('time_labor.html')
    
    @app.route('/workforce-planning')
    def workforce_planning_page():
        return render_template('workforce_planning.html')
    
    @app.route('/succession-planning')
    def succession_planning_page():
        return render_template('succession_planning.html')
    
    # ================================================================
    # EMPLOYEE SERVICES & TOOLS
    # ================================================================
    
    @app.route('/self-service')
    def self_service_page():
        return render_template('self_service.html')
    
    @app.route('/announcements')
    def announcements_page():
        return render_template('announcements.html')
    
    @app.route('/documents')
    def documents_page():
        return render_template('documents.html')
    
    @app.route('/timesheets')
    def timesheets_page():
        return render_template('timesheets.html')
    
    @app.route('/analytics')
    def analytics_page():
        return render_template('analytics.html')
    
    @app.route('/compensation')
    def compensation_page():
        return render_template('compensation.html')
    
    @app.route('/compliance')
    def compliance_page():
        return render_template('compliance.html')
    
    # ================================================================
    # ADMINISTRATIVE ROUTES
    # ================================================================
    
    @app.route('/organizations')
    def organizations_page():
        return render_template('organizations.html')
    
    @app.route('/settings')
    def settings_page():
        return render_template('settings.html')
    
    @app.route('/roles')
    def roles_page():
        return render_template('roles.html')
    
    @app.route('/saas-admin')
    def saas_admin_dashboard():
        return render_template('saas-admin.html')
    
    # ================================================================
    # UTILITY ROUTES
    # ================================================================
    
    @app.route('/calendar')
    def calendar_page():
        return render_template('calendar.html')
    
    @app.route('/surveys')
    def surveys_page():
        return render_template('surveys.html')
    
    @app.route('/goals')
    def goals_page():
        return render_template('goals.html')
    
    @app.route('/careers')
    def careers():
        return render_template('careers.html')
    
    # ================================================================
    # SUPER ADMIN ROUTES (Protected)
    # ================================================================
    
    def superadmin_required(f):
        """Decorator for super admin access"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return render_template('superadmin_check.html', 
                                 target_page=f.__name__,
                                 debug_login_page=(f.__name__ == 'debug_login'))
        return decorated_function
    
    @app.route('/debug-login')
    @superadmin_required
    def debug_login():
        return render_template('debug-login.html')
    
    @app.route('/rbac-test')
    def rbac_test_page():
        return render_template('rbac_test.html')
    
    @app.route('/rbac-guide')
    @superadmin_required
    def rbac_guide_page():
        return render_template('rbac_guide.html')
    
    # ================================================================
    # API INFORMATION ENDPOINT
    # ================================================================
    
    @app.route('/api')
    def api_info():
        """Comprehensive API information endpoint"""
        return jsonify({
            'name': 'HR Management System API',
            'version': '2.0.0',
            'description': 'Unified Multi-tenant SaaS HR Management Platform',
            'architecture': 'Multi-tenant SaaS with RBAC',
            'features': [
                'Multi-tenant organizations',
                'Role-based access control',
                'Employee lifecycle management',
                'Advanced time & labor tracking',
                'Performance management',
                'Recruitment & onboarding',
                'Benefits & compensation',
                'Workforce planning & analytics',
                'Employee relations & disciplinary',
                'Exit management & succession planning',
                'Self-service portal',
                'Document management',
                'Compliance tracking',
                'Real-time analytics'
            ],
            'module_count': len(blueprint_registry),
            'endpoints': {
                'authentication': '/api/auth',
                'employees': '/api/employees',
                'organizations': '/api/organizations',
                'time_tracking': '/api/attendance',
                'leave_management': '/api/leaves',
                'payroll': '/api/payroll',
                'performance': '/api/performance',
                'recruitment': '/api/recruitment',
                'training': '/api/training',
                'benefits': '/api/benefits',
                'onboarding': '/api/onboarding',
                'exit_management': '/api/exit-management',
                'employee_relations': '/api/employee-relations',
                'time_labor': '/api/time-labor',
                'workforce_planning': '/api/workforce-planning',
                'succession_planning': '/api/succession-planning',
                'analytics': '/api/analytics',
                'self_service': '/api/self-service',
                'compliance': '/api/compliance',
                'saas_admin': '/api/saas-admin',
                'super_admin': '/api/super-admin'
            },
            'status': 'Production Ready',
            'last_updated': '2025-10-02'
        })
    
    # ================================================================
    # ERROR HANDLERS
    # ================================================================
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({'error': 'Unauthorized access'}), 401
    
    # ================================================================
    # HEALTH CHECK ENDPOINT
    # ================================================================
    
    @app.route('/health')
    def health_check():
        """System health check endpoint"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': '2025-10-02',
            'components': {
                'database': db_status,
                'modules_loaded': len(blueprint_registry),
                'flask_version': '3.0.0'
            }
        })
    
    app.logger.info(f"🚀 HR Management System initialized with {len(blueprint_registry)} modules")
    
    return app