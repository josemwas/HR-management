import os
from app import create_app, db
from app.models import Employee, Department, Attendance, Leave, Payroll, JobPosting, Applicant, PerformanceReview

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Employee': Employee,
        'Department': Department,
        'Attendance': Attendance,
        'Leave': Leave,
        'Payroll': Payroll,
        'JobPosting': JobPosting,
        'Applicant': Applicant,
        'PerformanceReview': PerformanceReview
    }

@app.route('/')
def index():
    return {
        'message': 'Welcome to HR Management System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'employees': '/api/employees',
            'attendance': '/api/attendance',
            'leaves': '/api/leaves',
            'payroll': '/api/payroll',
            'recruitment': '/api/recruitment',
            'performance': '/api/performance'
        }
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
