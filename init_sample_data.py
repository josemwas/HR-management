"""
Script to initialize the database with sample data for testing
Run this after setting up the database
"""
import os
from datetime import date, timedelta
from app import create_app, db
from app.models import Employee, Department, Attendance, Leave, Payroll, JobPosting, Applicant, PerformanceReview

def init_sample_data():
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Clear existing data (be careful in production!)
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create Departments
        print("Creating departments...")
        departments = [
            Department(name='IT', description='Information Technology Department'),
            Department(name='HR', description='Human Resources Department'),
            Department(name='Finance', description='Finance Department'),
            Department(name='Sales', description='Sales Department'),
            Department(name='Marketing', description='Marketing Department')
        ]
        for dept in departments:
            db.session.add(dept)
        db.session.commit()
        
        # Create Employees
        print("Creating employees...")
        employees_data = [
            {
                'employee_id': 'ADMIN001',
                'email': 'admin@company.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'position': 'System Administrator',
                'department_id': 1,
                'salary': 100000,
                'role': 'admin'
            },
            {
                'employee_id': 'MGR001',
                'email': 'john.manager@company.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'position': 'IT Manager',
                'department_id': 1,
                'salary': 90000,
                'role': 'manager'
            },
            {
                'employee_id': 'EMP001',
                'email': 'jane.dev@company.com',
                'first_name': 'Jane',
                'last_name': 'Developer',
                'position': 'Software Engineer',
                'department_id': 1,
                'salary': 75000,
                'role': 'employee'
            },
            {
                'employee_id': 'EMP002',
                'email': 'bob.hr@company.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'position': 'HR Specialist',
                'department_id': 2,
                'salary': 65000,
                'role': 'employee'
            },
            {
                'employee_id': 'EMP003',
                'email': 'alice.fin@company.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'position': 'Financial Analyst',
                'department_id': 3,
                'salary': 70000,
                'role': 'employee'
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
                hire_date=date.today() - timedelta(days=365),
                status='active'
            )
            emp.set_password('password123')  # Default password for all
            db.session.add(emp)
            employees.append(emp)
        db.session.commit()
        
        # Create Attendance Records
        print("Creating attendance records...")
        for emp in employees:
            for i in range(5):
                attendance = Attendance(
                    employee_id=emp.id,
                    date=date.today() - timedelta(days=i),
                    check_in=None,
                    check_out=None,
                    status='present'
                )
                db.session.add(attendance)
        db.session.commit()
        
        # Create Leave Requests
        print("Creating leave requests...")
        leaves_data = [
            {
                'employee_id': employees[2].id,
                'leave_type': 'vacation',
                'start_date': date.today() + timedelta(days=30),
                'end_date': date.today() + timedelta(days=34),
                'days': 5,
                'reason': 'Family vacation',
                'status': 'pending'
            },
            {
                'employee_id': employees[3].id,
                'leave_type': 'sick',
                'start_date': date.today() - timedelta(days=2),
                'end_date': date.today() - timedelta(days=1),
                'days': 2,
                'reason': 'Flu',
                'status': 'approved',
                'approved_by': employees[1].id
            }
        ]
        
        for leave_data in leaves_data:
            leave = Leave(**leave_data)
            db.session.add(leave)
        db.session.commit()
        
        # Create Payroll Records
        print("Creating payroll records...")
        current_month = date.today().month
        current_year = date.today().year
        
        for emp in employees:
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
        db.session.commit()
        
        # Create Job Postings
        print("Creating job postings...")
        jobs = [
            {
                'title': 'Senior Software Engineer',
                'description': 'Looking for an experienced software engineer',
                'department_id': 1,
                'requirements': 'Python, Flask, 5+ years experience',
                'salary_range': '$80,000 - $100,000',
                'location': 'Remote',
                'employment_type': 'full-time',
                'status': 'open',
                'posted_by': employees[0].id,
                'posted_date': date.today()
            },
            {
                'title': 'HR Manager',
                'description': 'Experienced HR professional needed',
                'department_id': 2,
                'requirements': 'HR certification, 3+ years experience',
                'salary_range': '$70,000 - $90,000',
                'location': 'Hybrid',
                'employment_type': 'full-time',
                'status': 'open',
                'posted_by': employees[0].id,
                'posted_date': date.today()
            }
        ]
        
        for job_data in jobs:
            job = JobPosting(**job_data)
            db.session.add(job)
        db.session.commit()
        
        # Create Applicants
        print("Creating applicants...")
        applicants = [
            {
                'job_posting_id': 1,
                'first_name': 'Tom',
                'last_name': 'Anderson',
                'email': 'tom@example.com',
                'phone': '1234567890',
                'status': 'applied',
                'applied_date': date.today()
            },
            {
                'job_posting_id': 1,
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': 'sarah@example.com',
                'phone': '0987654321',
                'status': 'screening',
                'applied_date': date.today() - timedelta(days=2)
            }
        ]
        
        for app_data in applicants:
            applicant = Applicant(**app_data)
            db.session.add(applicant)
        db.session.commit()
        
        # Create Performance Reviews
        print("Creating performance reviews...")
        reviews = [
            {
                'employee_id': employees[2].id,
                'reviewer_id': employees[1].id,
                'review_period_start': date.today() - timedelta(days=90),
                'review_period_end': date.today(),
                'rating': 4.5,
                'goals_met': 'All quarterly goals achieved',
                'strengths': 'Strong technical skills, team player',
                'areas_for_improvement': 'Time management',
                'comments': 'Excellent performance overall',
                'status': 'submitted'
            }
        ]
        
        for review_data in reviews:
            review = PerformanceReview(**review_data)
            db.session.add(review)
        db.session.commit()
        
        print("\n✅ Sample data initialized successfully!")
        print("\nLogin Credentials:")
        print("=" * 50)
        print("Admin User:")
        print("  Email: admin@company.com")
        print("  Password: password123")
        print("\nManager User:")
        print("  Email: john.manager@company.com")
        print("  Password: password123")
        print("\nEmployee User:")
        print("  Email: jane.dev@company.com")
        print("  Password: password123")
        print("=" * 50)

if __name__ == '__main__':
    init_sample_data()
