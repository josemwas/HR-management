import os
from flask import render_template
from app import create_app, db
from app.models import Employee, Department, Attendance, Leave, Payroll, JobPosting, Applicant, PerformanceReview, Organization, SubscriptionPlan

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
        'PerformanceReview': PerformanceReview,
        'Organization': Organization,
        'SubscriptionPlan': SubscriptionPlan
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
