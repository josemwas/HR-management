from flask import Flask
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
    from app.routes import auth, employees, attendance, leaves, payroll, recruitment, performance, training, organizations, saas_admin, super_admin
    
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
    
    # Register frontend routes
    from flask import render_template, jsonify, request, redirect, url_for
    from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
    
    @app.route('/')
    def index():
        # Simply show the dashboard - let the frontend handle authentication
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
    
    @app.route('/debug-login')
    def debug_login():
        return render_template('debug-login.html')
    
    @app.route('/careers')
    def careers():
        return render_template('careers.html')
    
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
