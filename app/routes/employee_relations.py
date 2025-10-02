from flask import Blueprint, request, jsonify, current_app, render_template
from datetime import datetime, timedelta
import json

# Create blueprint
employee_relations_bp = Blueprint('employee_relations', __name__)

@employee_relations_bp.route('/employee-relations')
def employee_relations():
    """Employee Relations & Disciplinary Management dashboard"""
    return render_template('employee_relations.html')

# Sample data structures
class ERCase:
    def __init__(self, id, case_type, employees, description, priority='medium', 
                 status='open', assigned_to=None, reporter=None, incident_date=None):
        self.id = id
        self.case_type = case_type
        self.employees = employees
        self.description = description
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to
        self.reporter = reporter
        self.incident_date = incident_date
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.due_date = self.created_at + timedelta(days=self._get_due_days())
        self.resolution_notes = None
        self.documents = []

    def _get_due_days(self):
        priority_days = {'low': 30, 'medium': 14, 'high': 7, 'critical': 3}
        return priority_days.get(self.priority, 14)

class DisciplinaryAction:
    def __init__(self, id, employee_id, employee_name, action_type, violation, 
                 severity, description, issued_by, date_issued=None):
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.action_type = action_type
        self.violation = violation
        self.severity = severity
        self.description = description
        self.issued_by = issued_by
        self.date_issued = date_issued or datetime.now()
        self.status = 'active'
        self.follow_up_date = None
        self.completion_notes = None

class Grievance:
    def __init__(self, id, employee_id, employee_name, grievance_type, description, 
                 filed_date=None, priority='medium'):
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.grievance_type = grievance_type
        self.description = description
        self.filed_date = filed_date or datetime.now()
        self.priority = priority
        self.status = 'submitted'
        self.assigned_investigator = None
        self.investigation_notes = []
        self.resolution = None
        self.resolved_date = None

class MediationSession:
    def __init__(self, id, participants, mediator, issue_description, 
                 scheduled_date, session_type='in-person'):
        self.id = id
        self.participants = participants
        self.mediator = mediator
        self.issue_description = issue_description
        self.scheduled_date = scheduled_date
        self.session_type = session_type
        self.status = 'scheduled'
        self.outcome = None
        self.follow_up_required = False
        self.session_notes = None

# Sample data
er_cases = [
    ERCase("ER-2025-001", "Interpersonal Conflict", ["John Smith", "Sarah Johnson"], 
           "Ongoing communication issues between team members affecting productivity", 
           "high", "investigating", "HR Manager", "Team Lead", "2025-09-28"),
    ERCase("ER-2025-002", "Performance Issue", ["Mike Davis"], 
           "Consistent failure to meet project deadlines and quality standards", 
           "medium", "open", "Senior HR Specialist", "Project Manager", "2025-10-01"),
    ERCase("ER-2025-003", "Harassment Complaint", ["Alice Brown"], 
           "Allegations of inappropriate comments and behavior from supervisor", 
           "critical", "investigating", "External Investigator", "Alice Brown", "2025-09-25"),
    ERCase("ER-2025-004", "Policy Violation", ["Robert Wilson"], 
           "Unauthorized access to confidential client information", 
           "high", "open", "HR Manager", "IT Security", "2025-10-02"),
    ERCase("ER-2025-005", "Discrimination", ["Lisa Brown"], 
           "Claims of unfair treatment based on gender in promotion decisions", 
           "critical", "investigating", "External Investigator", "Lisa Brown", "2025-09-30"),
]

disciplinary_actions = [
    DisciplinaryAction(1, 101, "Robert Wilson", "Written Warning", "Tardiness", 
                      "low", "Consistent late arrivals affecting team schedule", 
                      "HR Manager", datetime(2025, 9, 15)),
    DisciplinaryAction(2, 102, "Lisa Brown", "Suspension", "Policy Violation", 
                      "high", "Unauthorized disclosure of confidential information", 
                      "HR Director", datetime(2025, 9, 10)),
    DisciplinaryAction(3, 103, "Tom Anderson", "Final Warning", "Inappropriate Behavior", 
                      "high", "Verbal altercation with colleague in public area", 
                      "HR Manager", datetime(2025, 9, 20)),
    DisciplinaryAction(4, 104, "Jennifer Davis", "Verbal Warning", "Dress Code Violation", 
                      "low", "Repeated violations of company dress code policy", 
                      "Department Manager", datetime(2025, 9, 25)),
    DisciplinaryAction(5, 105, "David Miller", "Performance Improvement Plan", "Poor Performance", 
                      "medium", "Failure to meet sales targets for three consecutive quarters", 
                      "Sales Manager", datetime(2025, 9, 12)),
]

grievances = [
    Grievance("GR-2025-001", 201, "Jennifer Davis", "Workplace Discrimination", 
             "Alleging discriminatory treatment in work assignments and opportunities", 
             datetime(2025, 9, 25), "high"),
    Grievance("GR-2025-002", 202, "David Miller", "Unfair Treatment", 
             "Concerns about inconsistent application of company policies", 
             datetime(2025, 9, 20), "medium"),
    Grievance("GR-2025-003", 203, "Maria Rodriguez", "Harassment", 
             "Multiple incidents of verbal harassment from team members", 
             datetime(2025, 9, 18), "critical"),
    Grievance("GR-2025-004", 204, "Kevin Chen", "Retaliation", 
             "Claims of retaliation after reporting safety concerns", 
             datetime(2025, 9, 22), "high"),
]

# Set some grievances as resolved with investigators
grievances[1].status = 'resolved'
grievances[1].assigned_investigator = 'Senior HR Specialist'
grievances[1].resolved_date = datetime(2025, 10, 1)
grievances[1].resolution = 'Policy clarification provided and training scheduled'

mediation_sessions = [
    MediationSession(1, ["John Smith", "Sarah Johnson"], "HR Manager", 
                    "Workplace communication conflict affecting team dynamics", 
                    "2025-10-10 14:00", "in-person"),
    MediationSession(2, ["Mike Davis", "Project Manager"], "External Mediator", 
                    "Performance expectations disagreement and goal alignment", 
                    "2025-10-05 10:00", "video-call"),
    MediationSession(3, ["Tom Anderson", "Team Member"], "Senior HR Specialist", 
                    "Conflict resolution following disciplinary action", 
                    "2025-10-08 15:30", "in-person"),
]

# Set some sessions as completed
mediation_sessions[1].status = 'completed'
mediation_sessions[1].outcome = 'Mutual agreement reached on performance goals and communication protocol'
mediation_sessions[1].session_notes = 'Both parties committed to weekly check-ins and clear expectation setting'

# API Routes

@employee_relations_bp.route('/api/employee-relations/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get employee relations dashboard statistics"""
    try:
        open_cases = len([case for case in er_cases if case.status in ['open', 'investigating']])
        high_priority_cases = len([case for case in er_cases if case.priority in ['high', 'critical']])
        resolved_this_month = len([case for case in er_cases if case.status == 'resolved'])
        
        # Calculate average resolution time (mock calculation)
        avg_resolution_days = 12
        
        return jsonify({
            'success': True,
            'data': {
                'open_cases': open_cases,
                'high_priority_cases': high_priority_cases,
                'resolved_this_month': resolved_this_month,
                'avg_resolution_days': avg_resolution_days,
                'total_cases_ytd': len(er_cases),
                'disciplinary_actions_active': len([d for d in disciplinary_actions if d.status == 'active']),
                'grievances_pending': len([g for g in grievances if g.status != 'resolved'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/cases', methods=['GET'])
def get_er_cases():
    """Get all employee relations cases with optional filtering"""
    try:
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        case_type_filter = request.args.get('case_type')
        
        filtered_cases = er_cases
        
        if status_filter:
            filtered_cases = [c for c in filtered_cases if c.status == status_filter]
        
        if priority_filter:
            filtered_cases = [c for c in filtered_cases if c.priority == priority_filter]
            
        if case_type_filter:
            filtered_cases = [c for c in filtered_cases if c.case_type == case_type_filter]
        
        cases_data = []
        for case in filtered_cases:
            cases_data.append({
                'id': case.id,
                'case_type': case.case_type,
                'employees': case.employees,
                'description': case.description,
                'priority': case.priority,
                'status': case.status,
                'assigned_to': case.assigned_to,
                'reporter': case.reporter,
                'incident_date': case.incident_date,
                'created_at': case.created_at.isoformat(),
                'updated_at': case.updated_at.isoformat(),
                'due_date': case.due_date.isoformat(),
                'resolution_notes': case.resolution_notes,
                'documents': case.documents
            })
        
        return jsonify({
            'success': True,
            'data': cases_data,
            'total': len(cases_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/cases', methods=['POST'])
def create_er_case():
    """Create a new employee relations case"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['case_type', 'employees', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Generate new case ID
        case_number = len(er_cases) + 1
        new_id = f"ER-2025-{case_number:03d}"
        
        # Create new case
        new_case = ERCase(
            id=new_id,
            case_type=data['case_type'],
            employees=data['employees'],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            assigned_to=data.get('assigned_to'),
            reporter=data.get('reporter'),
            incident_date=data.get('incident_date')
        )
        
        er_cases.append(new_case)
        
        return jsonify({
            'success': True,
            'message': 'Employee relations case created successfully',
            'data': {
                'id': new_case.id,
                'case_type': new_case.case_type,
                'status': new_case.status,
                'priority': new_case.priority
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/cases/<case_id>', methods=['PUT'])
def update_er_case(case_id):
    """Update an employee relations case"""
    try:
        data = request.get_json()
        
        # Find the case
        case = next((c for c in er_cases if c.id == case_id), None)
        if not case:
            return jsonify({'success': False, 'error': 'Case not found'}), 404
        
        # Update fields
        if 'status' in data:
            case.status = data['status']
        if 'priority' in data:
            case.priority = data['priority']
        if 'assigned_to' in data:
            case.assigned_to = data['assigned_to']
        if 'resolution_notes' in data:
            case.resolution_notes = data['resolution_notes']
        
        case.updated_at = datetime.now()
        
        return jsonify({
            'success': True,
            'message': 'Case updated successfully',
            'data': {
                'id': case.id,
                'status': case.status,
                'updated_at': case.updated_at.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/disciplinary', methods=['GET'])
def get_disciplinary_actions():
    """Get all disciplinary actions"""
    try:
        employee_filter = request.args.get('employee')
        status_filter = request.args.get('status')
        
        filtered_actions = disciplinary_actions
        
        if employee_filter:
            filtered_actions = [d for d in filtered_actions if d.employee_name == employee_filter]
        
        if status_filter:
            filtered_actions = [d for d in filtered_actions if d.status == status_filter]
        
        actions_data = []
        for action in filtered_actions:
            actions_data.append({
                'id': action.id,
                'employee_id': action.employee_id,
                'employee_name': action.employee_name,
                'action_type': action.action_type,
                'violation': action.violation,
                'severity': action.severity,
                'description': action.description,
                'issued_by': action.issued_by,
                'date_issued': action.date_issued.isoformat(),
                'status': action.status,
                'follow_up_date': action.follow_up_date.isoformat() if action.follow_up_date else None,
                'completion_notes': action.completion_notes
            })
        
        return jsonify({
            'success': True,
            'data': actions_data,
            'total': len(actions_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/disciplinary', methods=['POST'])
def create_disciplinary_action():
    """Create a new disciplinary action"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'employee_name', 'action_type', 'violation', 'severity', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create new disciplinary action
        new_id = len(disciplinary_actions) + 1
        new_action = DisciplinaryAction(
            id=new_id,
            employee_id=data['employee_id'],
            employee_name=data['employee_name'],
            action_type=data['action_type'],
            violation=data['violation'],
            severity=data['severity'],
            description=data['description'],
            issued_by=data.get('issued_by', 'HR Manager')
        )
        
        disciplinary_actions.append(new_action)
        
        return jsonify({
            'success': True,
            'message': 'Disciplinary action created successfully',
            'data': {
                'id': new_action.id,
                'employee_name': new_action.employee_name,
                'action_type': new_action.action_type,
                'status': new_action.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/grievances', methods=['GET'])
def get_grievances():
    """Get all grievances"""
    try:
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        
        filtered_grievances = grievances
        
        if status_filter:
            filtered_grievances = [g for g in filtered_grievances if g.status == status_filter]
        
        if priority_filter:
            filtered_grievances = [g for g in filtered_grievances if g.priority == priority_filter]
        
        grievances_data = []
        for grievance in filtered_grievances:
            grievances_data.append({
                'id': grievance.id,
                'employee_id': grievance.employee_id,
                'employee_name': grievance.employee_name,
                'grievance_type': grievance.grievance_type,
                'description': grievance.description,
                'filed_date': grievance.filed_date.isoformat(),
                'priority': grievance.priority,
                'status': grievance.status,
                'assigned_investigator': grievance.assigned_investigator,
                'investigation_notes': grievance.investigation_notes,
                'resolution': grievance.resolution,
                'resolved_date': grievance.resolved_date.isoformat() if grievance.resolved_date else None
            })
        
        return jsonify({
            'success': True,
            'data': grievances_data,
            'total': len(grievances_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/grievances', methods=['POST'])
def file_grievance():
    """File a new grievance"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'employee_name', 'grievance_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Generate new grievance ID
        grievance_number = len(grievances) + 1
        new_id = f"GR-2025-{grievance_number:03d}"
        
        # Create new grievance
        new_grievance = Grievance(
            id=new_id,
            employee_id=data['employee_id'],
            employee_name=data['employee_name'],
            grievance_type=data['grievance_type'],
            description=data['description'],
            priority=data.get('priority', 'medium')
        )
        
        grievances.append(new_grievance)
        
        return jsonify({
            'success': True,
            'message': 'Grievance filed successfully',
            'data': {
                'id': new_grievance.id,
                'employee_name': new_grievance.employee_name,
                'grievance_type': new_grievance.grievance_type,
                'status': new_grievance.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/mediation', methods=['GET'])
def get_mediation_sessions():
    """Get all mediation sessions"""
    try:
        status_filter = request.args.get('status')
        
        filtered_sessions = mediation_sessions
        
        if status_filter:
            filtered_sessions = [m for m in filtered_sessions if m.status == status_filter]
        
        sessions_data = []
        for session in filtered_sessions:
            sessions_data.append({
                'id': session.id,
                'participants': session.participants,
                'mediator': session.mediator,
                'issue_description': session.issue_description,
                'scheduled_date': session.scheduled_date,
                'session_type': session.session_type,
                'status': session.status,
                'outcome': session.outcome,
                'follow_up_required': session.follow_up_required,
                'session_notes': session.session_notes
            })
        
        return jsonify({
            'success': True,
            'data': sessions_data,
            'total': len(sessions_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/mediation', methods=['POST'])
def schedule_mediation():
    """Schedule a new mediation session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['participants', 'mediator', 'issue_description', 'scheduled_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create new mediation session
        new_id = len(mediation_sessions) + 1
        new_session = MediationSession(
            id=new_id,
            participants=data['participants'],
            mediator=data['mediator'],
            issue_description=data['issue_description'],
            scheduled_date=data['scheduled_date'],
            session_type=data.get('session_type', 'in-person')
        )
        
        mediation_sessions.append(new_session)
        
        return jsonify({
            'success': True,
            'message': 'Mediation session scheduled successfully',
            'data': {
                'id': new_session.id,
                'participants': new_session.participants,
                'scheduled_date': new_session.scheduled_date,
                'status': new_session.status
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@employee_relations_bp.route('/api/employee-relations/analytics', methods=['GET'])
def get_er_analytics():
    """Get employee relations analytics and trends"""
    try:
        # Case type distribution
        case_types = {}
        for case in er_cases:
            case_types[case.case_type] = case_types.get(case.case_type, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for case in er_cases:
            priority_distribution[case.priority] = priority_distribution.get(case.priority, 0) + 1
        
        # Resolution trends (mock data)
        monthly_resolution_trends = [
            {'month': 'Jan', 'opened': 5, 'resolved': 4},
            {'month': 'Feb', 'opened': 7, 'resolved': 6},
            {'month': 'Mar', 'opened': 6, 'resolved': 8},
            {'month': 'Apr', 'opened': 4, 'resolved': 5},
            {'month': 'May', 'opened': 9, 'resolved': 7},
            {'month': 'Jun', 'opened': 8, 'resolved': 9},
            {'month': 'Jul', 'opened': 6, 'resolved': 7},
            {'month': 'Aug', 'opened': 7, 'resolved': 6},
            {'month': 'Sep', 'opened': 5, 'resolved': 5},
            {'month': 'Oct', 'opened': 3, 'resolved': 4}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'case_type_distribution': case_types,
                'priority_distribution': priority_distribution,
                'monthly_trends': monthly_resolution_trends,
                'total_cases': len(er_cases),
                'open_cases': len([c for c in er_cases if c.status in ['open', 'investigating']]),
                'average_resolution_time': 12,
                'escalation_rate': 15.5,
                'employee_satisfaction_score': 4.1
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
