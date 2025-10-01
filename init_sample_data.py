"""
Script to initialize the database with sample data for the SaaS HR Management System
Run this after setting up the database
"""
import os
from datetime import date, datetime, timedelta
from app import create_app, db
from app.models.organization import Organization, SubscriptionPlan
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.models.payroll import Payroll
from app.models.recruitment import JobPosting, Applicant
from app.models.performance import PerformanceReview
from werkzeug.security import generate_password_hash

def init_sample_data():
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Clear existing data (be careful in production!)
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create Subscription Plans
        print("Creating subscription plans...")
        plans = [
            SubscriptionPlan(
                name='Free Trial',
                slug='trial',
                price_monthly=0,
                employee_limit=5,
                storage_limit_gb=1,
                api_calls_per_month=1000,
                trial_days=30,
                features={'basic': True}
            ),
            SubscriptionPlan(
                name='Starter',
                slug='starter',
                price_monthly=19,
                employee_limit=25,
                storage_limit_gb=10,
                api_calls_per_month=10000,
                trial_days=14,
                features={'basic': True, 'attendance': True}
            ),
            SubscriptionPlan(
                name='Professional',
                slug='professional',
                price_monthly=49,
                employee_limit=100,
                storage_limit_gb=50,
                api_calls_per_month=50000,
                trial_days=14,
                features={'basic': True, 'attendance': True, 'payroll': True, 'performance': True}
            ),
            SubscriptionPlan(
                name='Enterprise',
                slug='enterprise',
                price_monthly=99,
                employee_limit=1000,
                storage_limit_gb=200,
                api_calls_per_month=200000,
                trial_days=14,
                features={'basic': True, 'attendance': True, 'payroll': True, 'performance': True, 'recruitment': True, 'training': True}
            )
        ]
        
        for plan in plans:
            db.session.add(plan)
        db.session.commit()
        
        # Create Organizations
        print("Creating organizations...")
        organizations = [
            Organization(
                name='Acme Corporation',
                slug='acme-corp',
                email='admin@acme-corp.com',
                phone='+1-555-0123',
                address='123 Business St, NY 10001',
                website='https://acme-corp.com',
                industry='technology',
                size='51-200',
                plan_id=plans[2].id,  # Professional plan
                subscription_status='active',
                trial_start_date=date.today() - timedelta(days=60),
                trial_end_date=date.today() - timedelta(days=46),
                subscription_start_date=date.today() - timedelta(days=45),
                billing_email='billing@acme-corp.com',
                feature_settings={
                    'employee_management': True,
                    'attendance_tracking': True,
                    'leave_management': True,
                    'payroll_processing': True,
                    'performance_reviews': True,
                    'recruitment': False,
                    'training_development': False,
                    'analytics_reporting': True
                },
                is_active=True
            ),
            Organization(
                name='TechStartup Inc',
                slug='techstartup',
                email='admin@techstartup.com',
                phone='+1-555-0124',
                industry='technology',
                size='11-50',
                plan_id=plans[1].id,  # Starter plan
                subscription_status='active',
                trial_start_date=date.today() - timedelta(days=30),
                trial_end_date=date.today() - timedelta(days=16),
                subscription_start_date=date.today() - timedelta(days=15),
                billing_email='billing@techstartup.com',
                feature_settings={
                    'employee_management': True,
                    'attendance_tracking': True,
                    'leave_management': True,
                    'payroll_processing': False,
                    'performance_reviews': False,
                    'recruitment': False,
                    'training_development': False,
                    'analytics_reporting': True
                },
                is_active=True
            ),
            Organization(
                name='Global Enterprises',
                slug='global-ent',
                email='admin@global-ent.com',
                phone='+1-555-0125',
                industry='manufacturing',
                size='201-1000',
                plan_id=plans[3].id,  # Enterprise plan
                subscription_status='active',
                trial_start_date=date.today() - timedelta(days=90),
                trial_end_date=date.today() - timedelta(days=76),
                subscription_start_date=date.today() - timedelta(days=75),
                billing_email='billing@global-ent.com',
                feature_settings={
                    'employee_management': True,
                    'attendance_tracking': True,
                    'leave_management': True,
                    'payroll_processing': True,
                    'performance_reviews': True,
                    'recruitment': True,
                    'training_development': True,
                    'analytics_reporting': True
                },
                is_active=True
            )
        ]
        
        for org in organizations:
            db.session.add(org)
        db.session.commit()
        
        # Create Super Admin (cross-organization)
        print("Creating super admin...")
        super_admin = Employee(
            employee_id='SUPER001',
            email='superadmin@hrms.com',
            first_name='Super',
            last_name='Admin',
            phone='+1-555-ADMIN',
            position='System Administrator',
            role='super_admin',
            hire_date=date.today() - timedelta(days=365),
            status='active',
            organization_id=organizations[0].id,  # Assign to first org but with super_admin role
            password_hash=generate_password_hash('superadmin123')
        )
        db.session.add(super_admin)
        
        # Create Departments for each organization
        print("Creating departments...")
        departments_data = [
            # Acme Corporation departments
            {'name': 'Human Resources', 'description': 'HR Department', 'org_id': organizations[0].id},
            {'name': 'Engineering', 'description': 'Software Development', 'org_id': organizations[0].id},
            {'name': 'Sales', 'description': 'Sales Department', 'org_id': organizations[0].id},
            {'name': 'Marketing', 'description': 'Marketing Department', 'org_id': organizations[0].id},
            
            # TechStartup Inc departments
            {'name': 'Development', 'description': 'Software Development', 'org_id': organizations[1].id},
            {'name': 'Operations', 'description': 'Operations Department', 'org_id': organizations[1].id},
            
            # Global Enterprises departments
            {'name': 'Operations', 'description': 'Operations Department', 'org_id': organizations[2].id},
            {'name': 'Manufacturing', 'description': 'Manufacturing Department', 'org_id': organizations[2].id},
            {'name': 'Quality Assurance', 'description': 'QA Department', 'org_id': organizations[2].id},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = Department(
                name=dept_data['name'],
                description=dept_data['description'],
                organization_id=dept_data['org_id']
            )
            db.session.add(dept)
            departments.append(dept)
        db.session.commit()
        
        # Create Employees for each organization
        print("Creating employees...")
        employees_data = [
            # Acme Corporation employees
            {
                'employee_id': 'ACME001',
                'email': 'admin@acme-corp.com',
                'first_name': 'John',
                'last_name': 'Admin',
                'position': 'HR Manager',
                'department_id': departments[0].id,
                'salary': 85000,
                'role': 'admin',
                'org_id': organizations[0].id
            },
            {
                'employee_id': 'ACME002',
                'email': 'jane.doe@acme-corp.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'position': 'Senior Developer',
                'department_id': departments[1].id,
                'salary': 95000,
                'role': 'manager',
                'org_id': organizations[0].id
            },
            {
                'employee_id': 'ACME003',
                'email': 'bob.smith@acme-corp.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'position': 'Software Engineer',
                'department_id': departments[1].id,
                'salary': 75000,
                'role': 'employee',
                'org_id': organizations[0].id
            },
            
            # TechStartup Inc employees
            {
                'employee_id': 'TECH001',
                'email': 'admin@techstartup.com',
                'first_name': 'Jane',
                'last_name': 'Manager',
                'position': 'CTO',
                'department_id': departments[4].id,
                'salary': 120000,
                'role': 'admin',
                'org_id': organizations[1].id
            },
            {
                'employee_id': 'TECH002',
                'email': 'dev1@techstartup.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'position': 'Full Stack Developer',
                'department_id': departments[4].id,
                'salary': 80000,
                'role': 'employee',
                'org_id': organizations[1].id
            },
            
            # Global Enterprises employees
            {
                'employee_id': 'GLOBAL001',
                'email': 'admin@global-ent.com',
                'first_name': 'Bob',
                'last_name': 'Director',
                'position': 'Operations Director',
                'department_id': departments[6].id,
                'salary': 110000,
                'role': 'admin',
                'org_id': organizations[2].id
            },
            {
                'employee_id': 'GLOBAL002',
                'email': 'manager@global-ent.com',
                'first_name': 'Alice',
                'last_name': 'Wilson',
                'position': 'Manufacturing Manager',
                'department_id': departments[7].id,
                'salary': 85000,
                'role': 'manager',
                'org_id': organizations[2].id
            }
        ]
        
        employees = []
        for emp_data in employees_data:
            emp = Employee(
                employee_id=emp_data['employee_id'],
                email=emp_data['email'],
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                position=emp_data['position'],
                department_id=emp_data['department_id'],
                salary=emp_data['salary'],
                role=emp_data['role'],
                organization_id=emp_data['org_id'],
                hire_date=date.today() - timedelta(days=200),
                status='active',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(emp)
            employees.append(emp)
        db.session.commit()
        
        print("\n✅ Sample data initialized successfully!")
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        print("\n🔑 SUPER ADMIN (Platform Management):")
        print("   Email: superadmin@hrms.com")
        print("   Password: superadmin123")
        print("   Access: Super Admin Dashboard")
        
        print("\n🏢 ORGANIZATION ADMINS:")
        print("   Acme Corp:")
        print("     Email: admin@acme-corp.com")
        print("     Password: admin123")
        print("     Organization: acme-corp")
        
        print("   TechStartup Inc:")
        print("     Email: admin@techstartup.com") 
        print("     Password: admin123")
        print("     Organization: techstartup")
        
        print("   Global Enterprises:")
        print("     Email: admin@global-ent.com")
        print("     Password: admin123")
        print("     Organization: global-ent")
        
        print("\n📊 ORGANIZATION STATUS:")
        for org in organizations:
            print(f"   {org.name} ({org.slug})")
            print(f"     Plan: {next(p.name for p in plans if p.id == org.plan_id)}")
            print(f"     Status: {org.subscription_status}")
            print(f"     Employee Count: {len([e for e in employees if e.organization_id == org.id])}")
        
        print("\n🚀 ACCESS THE APPLICATION:")
        print("   Main Login: http://127.0.0.1:5000/login")
        print("   Registration: http://127.0.0.1:5000/signup")
        print("   Super Admin: http://127.0.0.1:5000/saas-admin")
        print("="*60)

if __name__ == '__main__':
    init_sample_data()
