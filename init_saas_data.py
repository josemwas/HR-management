"""
Script to initialize SaaS data including subscription plans and sample organization
Run this after running the SaaS migration
"""
import os
from datetime import date, timedelta
from app import create_app, db
from app.models.organization import Organization, SubscriptionPlan, Subscription
from app.models.employee import Employee
from app.models.department import Department

def init_saas_data():
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        print("Initializing SaaS data...")
        
        # Create subscription plans if they don't exist
        print("Creating subscription plans...")
        
        plans_data = [
            {
                'name': 'Free',
                'slug': 'free',
                'description': 'Perfect for small teams getting started',
                'price_monthly': 0.0,
                'price_yearly': 0.0,
                'employee_limit': 5,
                'storage_limit_gb': 1,
                'api_calls_per_month': 1000,
                'trial_days': 0,
                'sort_order': 1,
                'features': {
                    'employee_management': True,
                    'attendance_tracking': True,
                    'basic_reports': True,
                    'email_support': True,
                    'api_access': False,
                    'custom_branding': False,
                    'advanced_reports': False,
                    'integrations': False,
                    'priority_support': False
                }
            },
            {
                'name': 'Starter',
                'slug': 'starter',
                'description': 'Ideal for growing teams',
                'price_monthly': 29.0,
                'price_yearly': 290.0,
                'employee_limit': 25,
                'storage_limit_gb': 5,
                'api_calls_per_month': 5000,
                'trial_days': 14,
                'sort_order': 2,
                'features': {
                    'employee_management': True,
                    'attendance_tracking': True,
                    'basic_reports': True,
                    'email_support': True,
                    'api_access': True,
                    'custom_branding': False,
                    'advanced_reports': True,
                    'integrations': False,
                    'priority_support': False
                }
            },
            {
                'name': 'Professional',
                'slug': 'professional',
                'description': 'Complete solution for medium businesses',
                'price_monthly': 99.0,
                'price_yearly': 990.0,
                'employee_limit': 100,
                'storage_limit_gb': 25,
                'api_calls_per_month': 25000,
                'trial_days': 14,
                'is_popular': True,
                'sort_order': 3,
                'features': {
                    'employee_management': True,
                    'attendance_tracking': True,
                    'basic_reports': True,
                    'email_support': True,
                    'api_access': True,
                    'custom_branding': True,
                    'advanced_reports': True,
                    'integrations': True,
                    'priority_support': True
                }
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'description': 'Advanced features for large organizations',
                'price_monthly': 299.0,
                'price_yearly': 2990.0,
                'employee_limit': 1000,
                'storage_limit_gb': 100,
                'api_calls_per_month': 100000,
                'trial_days': 30,
                'sort_order': 4,
                'features': {
                    'employee_management': True,
                    'attendance_tracking': True,
                    'basic_reports': True,
                    'email_support': True,
                    'api_access': True,
                    'custom_branding': True,
                    'advanced_reports': True,
                    'integrations': True,
                    'priority_support': True,
                    'dedicated_support': True,
                    'sso': True,
                    'advanced_security': True,
                    'custom_fields': True
                }
            }
        ]
        
        created_plans = []
        for plan_data in plans_data:
            existing_plan = SubscriptionPlan.query.filter_by(slug=plan_data['slug']).first()
            if not existing_plan:
                plan = SubscriptionPlan(**plan_data)
                db.session.add(plan)
                created_plans.append(plan_data['name'])
        
        db.session.commit()
        print(f"Created plans: {', '.join(created_plans) if created_plans else 'All plans already exist'}")
        
        # Create a sample organization if none exists
        if Organization.query.count() == 0:
            print("Creating sample organization...")
            
            starter_plan = SubscriptionPlan.query.filter_by(slug='starter').first()
            
            # Create sample organization
            sample_org = Organization(
                name='Sample Company',
                slug='sample-company',
                email='admin@sample-company.com',
                phone='+1-555-0123',
                address='123 Business Street, City, State 12345',
                website='https://sample-company.com',
                industry='technology',
                size='11-50',
                plan_id=starter_plan.id,
                subscription_status='trial',
                trial_start_date=date.today(),
                trial_end_date=date.today() + timedelta(days=14),
                employee_limit=starter_plan.employee_limit,
                storage_limit_gb=starter_plan.storage_limit_gb,
                current_employee_count=0,
                current_storage_gb=0.0,
                billing_email='billing@sample-company.com'
            )
            
            db.session.add(sample_org)
            db.session.flush()  # Get the organization ID
            
            # Create sample departments
            departments = [
                Department(organization_id=sample_org.id, name='IT', description='Information Technology Department'),
                Department(organization_id=sample_org.id, name='HR', description='Human Resources Department'),
                Department(organization_id=sample_org.id, name='Finance', description='Finance Department')
            ]
            
            for dept in departments:
                db.session.add(dept)
            
            db.session.flush()
            
            # Create sample admin user
            admin_user = Employee(
                organization_id=sample_org.id,
                employee_id='ADMIN001',
                email='admin@sample-company.com',
                first_name='Admin',
                last_name='User',
                position='System Administrator',
                department_id=departments[0].id,  # IT department
                salary=100000,
                hire_date=date.today(),
                role='admin',
                status='active'
            )
            admin_user.set_password('password123')
            
            db.session.add(admin_user)
            
            # Update organization employee count
            sample_org.current_employee_count = 1
            
            db.session.commit()
            print("Sample organization 'Sample Company' created successfully")
            print("Admin login: admin@sample-company.com / password123")
        
        # Create super admin if specified
        super_admin_email = os.getenv('SUPER_ADMIN_EMAIL', 'superadmin@hrms.com')
        super_admin_password = os.getenv('SUPER_ADMIN_PASSWORD', 'superadmin123')
        
        # Check if super admin organization exists
        super_admin_org = Organization.query.filter_by(slug='saas-admin').first()
        if not super_admin_org:
            print("Creating super admin organization...")
            
            free_plan = SubscriptionPlan.query.filter_by(slug='free').first()
            
            super_admin_org = Organization(
                name='SaaS Admin',
                slug='saas-admin',
                email='admin@saas-admin.com',
                plan_id=free_plan.id,
                subscription_status='active',
                employee_limit=10,
                storage_limit_gb=10,
                current_employee_count=0,
                current_storage_gb=0.0
            )
            
            db.session.add(super_admin_org)
            db.session.flush()
            
            # Create admin department
            admin_dept = Department(
                organization_id=super_admin_org.id,
                name='Administration',
                description='SaaS Administration Department'
            )
            db.session.add(admin_dept)
            db.session.flush()
            
            # Create super admin user
            super_admin = Employee(
                organization_id=super_admin_org.id,
                employee_id='SUPERADMIN001',
                email=super_admin_email,
                first_name='Super',
                last_name='Admin',
                position='SaaS Administrator',
                department_id=admin_dept.id,
                salary=150000,
                hire_date=date.today(),
                role='super_admin',
                status='active'
            )
            super_admin.set_password(super_admin_password)
            
            db.session.add(super_admin)
            
            # Update organization employee count
            super_admin_org.current_employee_count = 1
            
            db.session.commit()
            print(f"Super admin created: {super_admin_email} / {super_admin_password}")
        
        print("\nSaaS initialization completed successfully!")
        print("\nAvailable logins:")
        print("1. Sample Organization Admin: admin@sample-company.com / password123")
        print(f"2. Super Admin: {super_admin_email} / {super_admin_password}")
        print("\nAccess points:")
        print("- Main application: http://localhost:5000/")
        print("- Organization signup: http://localhost:5000/signup")
        print("- SaaS admin dashboard: http://localhost:5000/saas-admin")
        print("- API documentation: http://localhost:5000/api")


if __name__ == '__main__':
    init_saas_data()