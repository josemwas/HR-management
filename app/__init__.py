from flask import Flask, render_template, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    # Set template and static folders relative to the project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import auth, employees, attendance, leaves, payroll, recruitment, performance, training, organizations, saas_admin, super_admin, rbac
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(leaves.bp)
    app.register_blueprint(payroll.bp)
    app.register_blueprint(recruitment.bp)
    app.register_blueprint(performance.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(organizations.bp)
    app.register_blueprint(saas_admin.bp)
    app.register_blueprint(super_admin.bp)
    app.register_blueprint(rbac.rbac_bp)
    
    # Register frontend routes
    from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
    
    @app.route('/')
    def index():
        # Redirect to login page as homepage
        return redirect('/login')
    
    @app.route('/dashboard')
    def dashboard():
        # The actual dashboard that requires authentication
        return render_template('dashboard.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/signup')
    def signup():
        return render_template('signup.html')
    
    @app.route('/saas-admin')
    def saas_admin_dashboard():
        return render_template('saas-admin.html')
    
    def superadmin_required(f):
        """Decorator to require superadmin access"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Return a page that will check authentication client-side
            # This approach works better with SPA-style authentication
            return render_template('superadmin_check.html', 
                                 target_page=f.__name__,
                                 debug_login_page=(f.__name__ == 'debug_login'),
                                 rbac_guide_page=(f.__name__ == 'rbac_guide_page'))
        
        return decorated_function
    
    @app.route('/debug-login')
    @superadmin_required
    def debug_login():
        return render_template('debug-login.html')
    
    @app.route('/careers')
    def careers():
        return render_template('careers.html')
    
    # Feature routes - dedicated functional pages
    @app.route('/employees')
    def employees_page():
        return render_template('employees.html')
    
    @app.route('/departments')
    def departments_page():
        return render_template('dashboard.html')  # Will create dedicated page
    
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
        return render_template('training.html')  # Create dedicated page
    
    @app.route('/benefits')
    def benefits_page():
        return render_template('benefits.html')
    
    @app.route('/onboarding')
    def onboarding_page():
        return render_template('onboarding.html')
    
    @app.route('/announcements')
    def announcements_page():
        return render_template('announcements.html')
    
    @app.route('/documents')
    def documents_page():
        return render_template('documents.html')
    
    @app.route('/calendar')
    def calendar_page():
        return render_template('calendar.html')
    
    @app.route('/analytics')
    def analytics_page():
        return render_template('analytics.html')
    
    @app.route('/timesheets')
    def timesheets_page():
        return render_template('timesheets.html')
    
    @app.route('/surveys')
    def surveys_page():
        return render_template('surveys.html')
    
    @app.route('/goals')
    def goals_page():
        return render_template('goals.html')
    
    @app.route('/settings')
    def settings_page():
        return render_template('settings.html')
    
    @app.route('/roles')
    def roles_page():
        return render_template('roles.html')
    
    @app.route('/rbac-test')
    def rbac_test_page():
        return render_template('rbac_test.html')
    
    @app.route('/rbac-guide')
    @superadmin_required
    def rbac_guide_page():
        return render_template('rbac_guide.html')
    
    @app.route('/organizations')
    def organizations_page():
        return render_template('organizations.html')
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'HR Management System API',
            'version': '1.0.0',
            'description': 'Multi-tenant SaaS HR Management System',
            'features': [
                'Multi-tenant organizations',
                'Subscription management',
                'Employee management',
                'Attendance tracking',
                'Leave management',
                'Payroll processing',
                'Performance reviews',
                'Recruitment portal',
                'Training & development',
                'Benefits management',
                'Document management',
                'Usage analytics'
            ],
            'endpoints': {
                'auth': '/api/auth',
                'organizations': '/api/organizations',
                'employees': '/api/employees',
                'attendance': '/api/attendance',
                'leaves': '/api/leaves',
                'payroll': '/api/payroll',
                'recruitment': '/api/recruitment',
                'performance': '/api/performance',
                'training': '/api/training',
                'saas_admin': '/api/saas-admin',
                'super_admin': '/api/super-admin'
            }
        })
    
    return app
