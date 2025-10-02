from flask import Blueprint, request, jsonify, current_app, render_template
from datetime import datetime, timedelta
import json

# Create blueprint
exit_management_bp = Blueprint('exit_management', __name__)

@exit_management_bp.route('/exit-management')
def exit_management():
    """Exit Management dashboard"""
    return render_template('exit_management.html')

# Sample data structures
class ExitProcess:
    def __init__(self, id, employee_id, employee_name, department, position, exit_type, 
                 notice_date, last_working_day, reason, status='initiated', progress=0):
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.department = department
        self.position = position
        self.exit_type = exit_type
        self.notice_date = notice_date
        self.last_working_day = last_working_day
        self.reason = reason
        self.status = status
        self.progress = progress
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class ExitInterview:
    def __init__(self, id, exit_process_id, employee_name, scheduled_date, 
                 interviewer, interview_type='in-person', status='scheduled'):
        self.id = id
        self.exit_process_id = exit_process_id
        self.employee_name = employee_name
        self.scheduled_date = scheduled_date
        self.interviewer = interviewer
        self.interview_type = interview_type
        self.status = status
        self.feedback_score = None
        self.feedback_notes = None
        self.created_at = datetime.now()

class OffboardingTask:
    def __init__(self, id, name, description, department, assignee, status='pending', priority='medium'):
        self.id = id
        self.name = name
        self.description = description
        self.department = department
        self.assignee = assignee
        self.status = status
        self.priority = priority
        self.due_date = None
        self.completed_date = None

# Sample data
exit_processes = [
    ExitProcess(1, 101, "John Smith", "IT", "Senior Developer", "resignation", 
                "2025-09-25", "2025-10-15", "Career advancement opportunity", "in-progress", 65),
    ExitProcess(2, 102, "Sarah Johnson", "Marketing", "Marketing Specialist", "contract_end", 
                "2025-09-30", "2025-10-20", "Contract completion", "initiated", 25),
    ExitProcess(3, 103, "Mike Davis", "Finance", "Financial Analyst", "termination", 
                "2025-09-28", "2025-10-10", "Performance issues", "completed", 100),
    ExitProcess(4, 104, "Alice Brown", "HR", "HR Coordinator", "resignation", 
                "2025-09-20", "2025-10-05", "Better opportunity", "completed", 100),
    ExitProcess(5, 105, "Robert Wilson", "Operations", "Operations Manager", "retirement", 
                "2025-10-01", "2025-11-30", "Planned retirement", "initiated", 15),
]

exit_interviews = [
    ExitInterview(1, 1, "John Smith", "2025-10-12 14:00", "HR Manager", "in-person", "scheduled"),
    ExitInterview(2, 4, "Alice Brown", "2025-10-03 10:00", "Department Head", "video-call", "completed"),
    ExitInterview(3, 3, "Mike Davis", "2025-10-08 15:30", "Senior HR Specialist", "in-person", "completed"),
]

# Set feedback scores for completed interviews
exit_interviews[1].feedback_score = 4.2
exit_interviews[1].feedback_notes = "Positive feedback about team collaboration, concerns about career growth opportunities"
exit_interviews[2].feedback_score = 3.8
exit_interviews[2].feedback_notes = "Good experience overall, suggested improvements in management communication"

offboarding_tasks = [
    OffboardingTask(1, "Return company equipment", "Collect laptop, phone, and other IT equipment", "IT", "IT Support Team", "pending", "high"),
    OffboardingTask(2, "Revoke system access", "Disable all system accounts and access privileges", "IT", "System Administrator", "pending", "high"),
    OffboardingTask(3, "Collect ID badge and keys", "Retrieve company ID, office keys, and access cards", "Security", "Security Team", "pending", "medium"),
    OffboardingTask(4, "Process final payroll", "Calculate final pay, benefits, and outstanding expenses", "HR", "Payroll Team", "in-progress", "high"),
    OffboardingTask(5, "Knowledge transfer", "Document and transfer critical knowledge to team", "Department", "Direct Supervisor", "pending", "high"),
    OffboardingTask(6, "Exit interview", "Conduct comprehensive exit interview", "HR", "HR Manager", "pending", "medium"),
    OffboardingTask(7, "Return confidential documents", "Collect and secure all confidential materials", "Legal", "Legal Team", "completed", "medium"),
    OffboardingTask(8, "Update organizational chart", "Remove employee from org chart and systems", "HR", "HR Administrator", "pending", "low"),
    OffboardingTask(9, "Benefits transition", "Process COBRA, 401k rollover, and final benefits", "HR", "Benefits Administrator", "in-progress", "medium"),
    OffboardingTask(10, "Asset inventory", "Complete inventory of assigned company assets", "Operations", "Asset Manager", "pending", "medium"),
]

# API Routes

@exit_management_bp.route('/api/exit-management/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get exit management dashboard statistics"""
    try:
        pending_exits = len([e for e in exit_processes if e.status == 'initiated'])
        in_progress_exits = len([e for e in exit_processes if e.status == 'in-progress'])
        completed_exits = len([e for e in exit_processes if e.status == 'completed'])
        
        # Calculate average completion time (mock calculation)
        avg_completion_days = 5.2
        
        return jsonify({
            'success': True,
            'data': {
                'pending_exits': pending_exits,
                'in_progress_exits': in_progress_exits,
                'completed_exits': completed_exits,
                'avg_completion_days': avg_completion_days,
                'total_exits_this_month': len(exit_processes),
                'turnover_rate': 15.2
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/processes', methods=['GET'])
def get_exit_processes():
    """Get all exit processes with optional filtering"""
    try:
        status_filter = request.args.get('status')
        department_filter = request.args.get('department')
        
        filtered_processes = exit_processes
        
        if status_filter:
            filtered_processes = [e for e in filtered_processes if e.status == status_filter]
        
        if department_filter:
            filtered_processes = [e for e in filtered_processes if e.department == department_filter]
        
        processes_data = []
        for process in filtered_processes:
            processes_data.append({
                'id': process.id,
                'employee_id': process.employee_id,
                'employee_name': process.employee_name,
                'department': process.department,
                'position': process.position,
                'exit_type': process.exit_type,
                'notice_date': process.notice_date,
                'last_working_day': process.last_working_day,
                'reason': process.reason,
                'status': process.status,
                'progress': process.progress,
                'created_at': process.created_at.isoformat(),
                'updated_at': process.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': processes_data,
            'total': len(processes_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/processes', methods=['POST'])
def initiate_exit_process():
    """Initiate a new exit process"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'employee_name', 'department', 'exit_type', 'notice_date', 'last_working_day']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create new exit process
        new_id = len(exit_processes) + 1
        new_process = ExitProcess(
            id=new_id,
            employee_id=data['employee_id'],
            employee_name=data['employee_name'],
            department=data['department'],
            position=data.get('position', ''),
            exit_type=data['exit_type'],
            notice_date=data['notice_date'],
            last_working_day=data['last_working_day'],
            reason=data.get('reason', '')
        )
        
        exit_processes.append(new_process)
        
        return jsonify({
            'success': True,
            'message': 'Exit process initiated successfully',
            'data': {
                'id': new_process.id,
                'employee_name': new_process.employee_name,
                'status': new_process.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/processes/<int:process_id>', methods=['PUT'])
def update_exit_process(process_id):
    """Update an exit process"""
    try:
        data = request.get_json()
        
        # Find the process
        process = next((p for p in exit_processes if p.id == process_id), None)
        if not process:
            return jsonify({'success': False, 'error': 'Exit process not found'}), 404
        
        # Update fields
        if 'status' in data:
            process.status = data['status']
        if 'progress' in data:
            process.progress = data['progress']
        if 'reason' in data:
            process.reason = data['reason']
        
        process.updated_at = datetime.now()
        
        return jsonify({
            'success': True,
            'message': 'Exit process updated successfully',
            'data': {
                'id': process.id,
                'status': process.status,
                'progress': process.progress
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/interviews', methods=['GET'])
def get_exit_interviews():
    """Get all exit interviews"""
    try:
        interviews_data = []
        for interview in exit_interviews:
            interviews_data.append({
                'id': interview.id,
                'exit_process_id': interview.exit_process_id,
                'employee_name': interview.employee_name,
                'scheduled_date': interview.scheduled_date,
                'interviewer': interview.interviewer,
                'interview_type': interview.interview_type,
                'status': interview.status,
                'feedback_score': interview.feedback_score,
                'feedback_notes': interview.feedback_notes,
                'created_at': interview.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': interviews_data,
            'total': len(interviews_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/interviews', methods=['POST'])
def schedule_exit_interview():
    """Schedule a new exit interview"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['exit_process_id', 'employee_name', 'scheduled_date', 'interviewer']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create new interview
        new_id = len(exit_interviews) + 1
        new_interview = ExitInterview(
            id=new_id,
            exit_process_id=data['exit_process_id'],
            employee_name=data['employee_name'],
            scheduled_date=data['scheduled_date'],
            interviewer=data['interviewer'],
            interview_type=data.get('interview_type', 'in-person')
        )
        
        exit_interviews.append(new_interview)
        
        return jsonify({
            'success': True,
            'message': 'Exit interview scheduled successfully',
            'data': {
                'id': new_interview.id,
                'employee_name': new_interview.employee_name,
                'scheduled_date': new_interview.scheduled_date
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/interviews/<int:interview_id>/feedback', methods=['POST'])
def submit_interview_feedback():
    """Submit feedback for an exit interview"""
    try:
        data = request.get_json()
        
        # Find the interview
        interview = next((i for i in exit_interviews if i.id == interview_id), None)
        if not interview:
            return jsonify({'success': False, 'error': 'Interview not found'}), 404
        
        # Update feedback
        interview.feedback_score = data.get('feedback_score')
        interview.feedback_notes = data.get('feedback_notes')
        interview.status = 'completed'
        
        return jsonify({
            'success': True,
            'message': 'Interview feedback submitted successfully',
            'data': {
                'id': interview.id,
                'feedback_score': interview.feedback_score,
                'status': interview.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/offboarding/tasks', methods=['GET'])
def get_offboarding_tasks():
    """Get offboarding checklist tasks"""
    try:
        exit_process_id = request.args.get('exit_process_id')
        status_filter = request.args.get('status')
        
        filtered_tasks = offboarding_tasks
        
        if status_filter:
            filtered_tasks = [t for t in filtered_tasks if t.status == status_filter]
        
        tasks_data = []
        for task in filtered_tasks:
            tasks_data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'department': task.department,
                'assignee': task.assignee,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date,
                'completed_date': task.completed_date.isoformat() if task.completed_date else None
            })
        
        return jsonify({
            'success': True,
            'data': tasks_data,
            'total': len(tasks_data),
            'summary': {
                'pending': len([t for t in filtered_tasks if t.status == 'pending']),
                'in_progress': len([t for t in filtered_tasks if t.status == 'in-progress']),
                'completed': len([t for t in filtered_tasks if t.status == 'completed'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/offboarding/tasks/<int:task_id>', methods=['PUT'])
def update_offboarding_task(task_id):
    """Update an offboarding task"""
    try:
        data = request.get_json()
        
        # Find the task
        task = next((t for t in offboarding_tasks if t.id == task_id), None)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Update fields
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_date = datetime.now()
        
        if 'assignee' in data:
            task.assignee = data['assignee']
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'data': {
                'id': task.id,
                'status': task.status,
                'completed_date': task.completed_date.isoformat() if task.completed_date else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/analytics', methods=['GET'])
def get_exit_analytics():
    """Get exit analytics and insights"""
    try:
        # Department turnover rates
        departments = ['IT', 'Marketing', 'Finance', 'HR', 'Operations']
        department_turnover = {
            'IT': 12.5,
            'Marketing': 18.3,
            'Finance': 8.7,
            'HR': 15.2,
            'Operations': 22.1
        }
        
        # Exit reasons distribution
        exit_reasons = {
            'Career Growth': 35,
            'Better Offer': 25,
            'Work-Life Balance': 20,
            'Management Issues': 12,
            'Other': 8
        }
        
        # Monthly exit trends
        monthly_exits = [
            {'month': 'Jan', 'exits': 8, 'hires': 12},
            {'month': 'Feb', 'exits': 6, 'hires': 10},
            {'month': 'Mar', 'exits': 10, 'hires': 15},
            {'month': 'Apr', 'exits': 7, 'hires': 9},
            {'month': 'May', 'exits': 12, 'hires': 14},
            {'month': 'Jun', 'exits': 9, 'hires': 11},
            {'month': 'Jul', 'exits': 11, 'hires': 13},
            {'month': 'Aug', 'exits': 8, 'hires': 16},
            {'month': 'Sep', 'exits': 5, 'hires': 8},
            {'month': 'Oct', 'exits': 4, 'hires': 7}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'overall_turnover_rate': 15.2,
                'average_replacement_cost': 45000,
                'average_exit_rating': 4.2,
                'department_turnover': department_turnover,
                'exit_reasons': exit_reasons,
                'monthly_trends': monthly_exits,
                'total_exits_ytd': 80,
                'total_hires_ytd': 115,
                'net_growth': 35
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@exit_management_bp.route('/api/exit-management/reports/turnover', methods=['GET'])
def generate_turnover_report():
    """Generate detailed turnover report"""
    try:
        start_date = request.args.get('start_date', '2025-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        department = request.args.get('department')
        
        # Filter data based on parameters
        filtered_exits = exit_processes
        if department:
            filtered_exits = [e for e in filtered_exits if e.department == department]
        
        report_data = {
            'period': {'start_date': start_date, 'end_date': end_date},
            'total_exits': len(filtered_exits),
            'voluntary_exits': len([e for e in filtered_exits if e.exit_type in ['resignation', 'retirement']]),
            'involuntary_exits': len([e for e in filtered_exits if e.exit_type == 'termination']),
            'department_breakdown': {},
            'exit_type_breakdown': {},
            'average_tenure': 2.8,  # years
            'replacement_costs': len(filtered_exits) * 45000
        }
        
        # Department breakdown
        for dept in ['IT', 'Marketing', 'Finance', 'HR', 'Operations']:
            dept_exits = [e for e in filtered_exits if e.department == dept]
            report_data['department_breakdown'][dept] = len(dept_exits)
        
        # Exit type breakdown
        for exit_type in ['resignation', 'termination', 'retirement', 'contract_end']:
            type_exits = [e for e in filtered_exits if e.exit_type == exit_type]
            report_data['exit_type_breakdown'][exit_type] = len(type_exits)
        
        return jsonify({
            'success': True,
            'data': report_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
