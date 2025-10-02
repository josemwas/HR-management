from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from datetime import datetime

bp = Blueprint('onboarding', __name__, url_prefix='/api/onboarding')

# Mock Onboarding model since we don't have it in the existing models
class OnboardingPlan:
    def __init__(self, id, employee_id, template_id, start_date, assigned_to, status, progress, current_task):
        self.id = id
        self.employee_id = employee_id
        self.template_id = template_id
        self.start_date = start_date
        self.assigned_to = assigned_to
        self.status = status
        self.progress = progress
        self.current_task = current_task
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'template_id': self.template_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'progress': self.progress,
            'current_task': self.current_task
        }

# Mock data for onboarding
mock_onboarding_plans = [
    OnboardingPlan(1, 1, 1, datetime(2024, 12, 15), 'IT Department', 'in_progress', 65, 'Complete IT setup'),
    OnboardingPlan(2, 2, 2, datetime(2024, 12, 18), 'HR Team', 'in_progress', 30, 'HR documentation'),
]

mock_templates = [
    {'id': 1, 'name': 'Software Developer', 'duration': 21, 'tasks': 15, 'status': 'active'},
    {'id': 2, 'name': 'Sales Representative', 'duration': 14, 'tasks': 12, 'status': 'active'},
    {'id': 3, 'name': 'Manager', 'duration': 30, 'tasks': 20, 'status': 'active'},
]

@bp.route('/plans', methods=['GET'])
@jwt_required()
def get_onboarding_plans():
    """Get all onboarding plans"""
    try:
        plans_data = []
        for plan in mock_onboarding_plans:
            plan_dict = plan.to_dict()
            # Add employee info
            employee = Employee.query.get(plan.employee_id)
            if employee:
                plan_dict['employee_name'] = f"{employee.first_name} {employee.last_name}"
                plan_dict['employee_email'] = employee.email
                plan_dict['department'] = employee.department.name if employee.department else 'N/A'
            plans_data.append(plan_dict)
        
        return jsonify(plans_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/plans', methods=['POST'])
@jwt_required()
def create_onboarding_plan():
    """Create a new onboarding plan"""
    try:
        data = request.json
        
        new_plan = OnboardingPlan(
            id=len(mock_onboarding_plans) + 1,
            employee_id=data.get('employee_id'),
            template_id=data.get('template_id'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d'),
            assigned_to=data.get('assigned_to'),
            status='draft',
            progress=0,
            current_task='Getting started'
        )
        
        mock_onboarding_plans.append(new_plan)
        
        return jsonify(new_plan.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_onboarding_plan(plan_id):
    """Get specific onboarding plan"""
    try:
        plan = next((p for p in mock_onboarding_plans if p.id == plan_id), None)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        plan_dict = plan.to_dict()
        # Add employee info
        employee = Employee.query.get(plan.employee_id)
        if employee:
            plan_dict['employee_name'] = f"{employee.first_name} {employee.last_name}"
            plan_dict['employee_email'] = employee.email
            plan_dict['department'] = employee.department.name if employee.department else 'N/A'
        
        return jsonify(plan_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_onboarding_plan(plan_id):
    """Update onboarding plan"""
    try:
        plan = next((p for p in mock_onboarding_plans if p.id == plan_id), None)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        data = request.json
        plan.status = data.get('status', plan.status)
        plan.progress = data.get('progress', plan.progress)
        plan.current_task = data.get('current_task', plan.current_task)
        
        return jsonify(plan.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Get onboarding templates"""
    try:
        return jsonify(mock_templates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/templates', methods=['POST'])
@jwt_required()
def create_template():
    """Create onboarding template"""
    try:
        data = request.json
        
        new_template = {
            'id': len(mock_templates) + 1,
            'name': data.get('name'),
            'duration': data.get('duration'),
            'tasks': data.get('tasks'),
            'status': 'active'
        }
        
        mock_templates.append(new_template)
        
        return jsonify(new_template), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_onboarding_stats():
    """Get onboarding statistics"""
    try:
        stats = {
            'active_plans': len([p for p in mock_onboarding_plans if p.status == 'in_progress']),
            'completed_month': 8,
            'in_progress': len([p for p in mock_onboarding_plans if p.status == 'in_progress']),
            'avg_completion': '14 days'
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500