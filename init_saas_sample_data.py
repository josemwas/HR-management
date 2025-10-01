"""
Script to initialize the SaaS database with sample data including organizations
Run this after setting up the database for SaaS mode
"""
import os
from datetime import date, timedelta, datetime
from app import create_app, db
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.models.payroll import Payroll
from app.models.recruitment import JobPosting, Applicant
from app.models.performance import PerformanceReview
from app.models.organization import Organization, SubscriptionPlan, Subscription

def init_saas_sample_data():
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
                name='Free',
                slug='free',
                description='Basic features for small teams',
                employee_limit=10,
                price_monthly=0.00,
                price_yearly=0.00,
                storage_limit_gb=1,
                features=['Basic employee management', 'Time tracking', 'Simple reporting']
            ),
            SubscriptionPlan(
                name='Starter',
                slug='starter',
                description='Perfect for growing teams',
                employee_limit=50,
                price_monthly=29.99,
                price_yearly=299.99,
                storage_limit_gb=5,
                features=['All Free features', 'Advanced reporting', 'Leave management', 'Basic payroll']
            ),
            SubscriptionPlan(
                name='Professional',
                slug='professional',
                description='Advanced features for medium businesses',
                employee_limit=200,
                price_monthly=99.99,
                price_yearly=999.99,
                storage_limit_gb=20,
                features=['All Starter features', 'Performance reviews', 'Recruitment tools', 'Advanced analytics']
            ),
            SubscriptionPlan(
                name='Enterprise',
                slug='enterprise',
                description='Full-featured solution for large organizations',
                employee_limit=1000,
                price_monthly=299.99,
                price_yearly=2999.99,
                storage_limit_gb=100,
                features=['All Professional features', 'Custom integrations', 'Priority support', 'Advanced security']
            )
        ]
        
        for plan in plans:
            db.session.add(plan)
        db.session.commit()
        
        # Create Organizations
        print("Creating organizations...")
        organizations = [
            {
                'name': 'Acme Corporation',
                'slug': 'acme',
                'email': 'admin@acme.com',
                'phone': '+1-555-0123',
                'address': '123 Business St, Suite 100, New York, NY 10001',
                'industry': 'Technology',
                'size': 'medium',
                'subscription_status': 'active',
                'plan_id': 2  # Starter plan
            },
            {
                'name': 'TechStartup Inc',
                'slug': 'techstartup',
                'email': 'hello@techstartup.com',
                'phone': '+1-555-0456',
                'address': '456 Innovation Ave, San Francisco, CA 94105',
                'industry': 'Software',
                'size': 'small',
                'subscription_status': 'active',
                'plan_id': 1  # Free plan
            },
            {
                'name': 'Global Enterprises LLC',
                'slug': 'globalent',
                'email': 'contact@globalent.com',
                'phone': '+1-555-0789',
                'address': '789 Enterprise Blvd, Chicago, IL 60601',
                'industry': 'Manufacturing',
                'size': 'large',
                'subscription_status': 'active',
                'plan_id': 3  # Professional plan
            }
        ]
        
        org_objects = []
        for org_data in organizations:
            org = Organization(**org_data)
            db.session.add(org)
            org_objects.append(org)
        db.session.commit()
        
        # Create Subscriptions for Organizations
        print("Creating subscriptions...")
        for i, org in enumerate(org_objects):
            plan = plans[org.plan_id-1]  # Get the plan object
            subscription = Subscription(
                organization_id=org.id,
                plan_id=org.plan_id,
                billing_cycle='monthly',
                amount=plan.price_monthly,
                status='active',
                start_date=datetime.utcnow().date(),
                end_date=datetime.utcnow().date() + timedelta(days=30),
                next_billing_date=datetime.utcnow().date() + timedelta(days=30)
            )
            db.session.add(subscription)
        db.session.commit()
        
        # Create Super Admin
        print("Creating super admin...")
        super_admin = Employee(
            employee_id='SUPER001',
            email='superadmin@hrmanagement.com',
            first_name='Super',
            last_name='Admin',
            position='Platform Administrator',
            salary=150000,
            role='super_admin',
            hire_date=date.today() - timedelta(days=730),
            status='active',
            organization_id=None  # Super admin doesn't belong to any organization
        )
        super_admin.set_password('superadmin123')
        db.session.add(super_admin)
        db.session.commit()
        
        # Create data for each organization
        for org_idx, org in enumerate(org_objects):
            print(f"Creating data for {org.name}...")
            
            # Create Departments for this organization
            departments_data = [
                {'name': 'IT', 'description': 'Information Technology Department'},
                {'name': 'HR', 'description': 'Human Resources Department'},
                {'name': 'Finance', 'description': 'Finance Department'},
                {'name': 'Sales', 'description': 'Sales Department'}
            ]
            
            org_departments = []
            for dept_data in departments_data:
                dept = Department(
                    name=dept_data['name'],
                    description=dept_data['description'],
                    organization_id=org.id
                )
                db.session.add(dept)
                org_departments.append(dept)
            db.session.commit()
            
            # Create Employees for this organization
            employees_data = [
                {
                    'employee_id': f'ORG{org_idx+1}_ADMIN001',
                    'email': f'admin@{org.email.split("@")[1]}',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'position': 'System Administrator',
                    'department_id': org_departments[0].id,
                    'salary': 100000,
                    'role': 'admin'
                },
                {
                    'employee_id': f'ORG{org_idx+1}_MGR001',
                    'email': f'manager@{org.email.split("@")[1]}',
                    'first_name': 'John',
                    'last_name': 'Manager',
                    'position': 'IT Manager',
                    'department_id': org_departments[0].id,
                    'salary': 90000,
                    'role': 'manager'
                },
                {
                    'employee_id': f'ORG{org_idx+1}_EMP001',
                    'email': f'employee1@{org.email.split("@")[1]}',
                    'first_name': 'Jane',
                    'last_name': 'Developer',
                    'position': 'Software Engineer',
                    'department_id': org_departments[0].id,
                    'salary': 75000,
                    'role': 'employee'
                },
                {
                    'employee_id': f'ORG{org_idx+1}_EMP002',
                    'email': f'employee2@{org.email.split("@")[1]}',
                    'first_name': 'Bob',
                    'last_name': 'Smith',
                    'position': 'HR Specialist',
                    'department_id': org_departments[1].id,
                    'salary': 65000,
                    'role': 'employee'
                }
            ]
            
            org_employees = []
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
                    hire_date=date.today() - timedelta(days=365),
                    status='active',
                    organization_id=org.id
                )
                emp.set_password('password123')  # Default password for all
                db.session.add(emp)
                org_employees.append(emp)
            db.session.commit()
            
            # Update department managers
            org_departments[0].manager_id = org_employees[1].id  # IT Manager
            org_departments[1].manager_id = org_employees[3].id  # HR Manager (employee 2)
            
            # Create some sample data for the first organization only (to keep it simple)
            if org_idx == 0:
                # Create Attendance Records
                print("Creating attendance records...")
                for emp in org_employees:
                    for i in range(5):
                        attendance = Attendance(
                            employee_id=emp.id,
                            date=date.today() - timedelta(days=i),
                            check_in=None,
                            check_out=None,
                            status='present'
                        )
                        db.session.add(attendance)
                
                # Create Leave Requests
                print("Creating leave requests...")
                leave = Leave(
                    employee_id=org_employees[2].id,
                    leave_type='vacation',
                    start_date=date.today() + timedelta(days=30),
                    end_date=date.today() + timedelta(days=34),
                    days=5,
                    reason='Family vacation',
                    status='pending'
                )
                db.session.add(leave)
                
                # Create Payroll Records
                print("Creating payroll records...")
                current_month = date.today().month
                current_year = date.today().year
                
                for emp in org_employees:
                    payroll = Payroll(
                        employee_id=emp.id,
                        month=current_month,
                        year=current_year,
                        basic_salary=emp.salary,
                        allowances=emp.salary * 0.1,
                        deductions=emp.salary * 0.05,
                        bonus=0,
                        net_salary=emp.salary + (emp.salary * 0.1) - (emp.salary * 0.05),
                        status='pending'
                    )
                    db.session.add(payroll)
                
                # Create Job Posting
                print("Creating job posting...")
                job = JobPosting(
                    title='Senior Software Engineer',
                    description='Looking for an experienced software engineer',
                    department_id=org_departments[0].id,
                    requirements='Python, Flask, 5+ years experience',
                    salary_range='$80,000 - $100,000',
                    location='Remote',
                    employment_type='full-time',
                    status='open',
                    posted_by=org_employees[0].id,
                    posted_date=date.today()
                )
                db.session.add(job)
                db.session.commit()
                
                # Create Applicant
                applicant = Applicant(
                    job_posting_id=job.id,
                    first_name='Tom',
                    last_name='Anderson',
                    email='tom@example.com',
                    phone='1234567890',
                    status='applied',
                    applied_date=date.today()
                )
                db.session.add(applicant)
                
                # Create Performance Review
                print("Creating performance review...")
                review = PerformanceReview(
                    employee_id=org_employees[2].id,
                    reviewer_id=org_employees[1].id,
                    review_period_start=date.today() - timedelta(days=90),
                    review_period_end=date.today(),
                    rating=4.5,
                    goals_met='All quarterly goals achieved',
                    strengths='Strong technical skills, team player',
                    areas_for_improvement='Time management',
                    comments='Excellent performance overall',
                    status='submitted'
                )
                db.session.add(review)
        
        db.session.commit()
        
        print("\n✅ SaaS sample data initialized successfully!")
        print("\nLogin Credentials:")
        print("=" * 60)
        print("🌟 SUPER ADMIN (Platform Administrator):")
        print("  Email: superadmin@hrmanagement.com")
        print("  Password: superadmin123")
        print("  Access: All organizations and platform admin features")
        print("\n🏢 ORGANIZATION ADMINS:")
        for i, org in enumerate(org_objects):
            print(f"\n  {org.name}:")
            print(f"    Email: admin@{org.email.split('@')[1]}")
            print(f"    Password: password123")
            print(f"    Plan: {plans[org.plan_id-1].name}")
        print("\n👥 SAMPLE EMPLOYEES (for each org):")
        print("  Manager: manager@[domain]")
        print("  Employee 1: employee1@[domain]")
        print("  Employee 2: employee2@[domain]")
        print("  Password: password123 (for all)")
        print("=" * 60)
        print("\n🚀 You can now:")
        print("1. Login as super admin to manage the platform")
        print("2. Login as organization admin to manage employees")
        print("3. Test the new SaaS features and organization isolation")
        print("4. Create new organizations via the signup page")

if __name__ == '__main__':
    init_saas_sample_data()