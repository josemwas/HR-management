from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

compliance = Blueprint('compliance', __name__)

# Mock Compliance classes
class ComplianceViolation:
    def __init__(self, id, type, description, severity, employee_id=None, department=None, status="open", created_date=None, due_date=None):
        self.id = id
        self.type = type
        self.description = description
        self.severity = severity
        self.employee_id = employee_id
        self.department = department
        self.status = status
        self.created_date = created_date or datetime.now()
        self.due_date = due_date

class ComplianceTraining:
    def __init__(self, id, name, required_for, completion_rate, due_date, category="general"):
        self.id = id
        self.name = name
        self.required_for = required_for
        self.completion_rate = completion_rate
        self.due_date = due_date
        self.category = category

class SafetyIncident:
    def __init__(self, id, incident_type, severity, description, employee_id, location, incident_date=None, status="open"):
        self.id = id
        self.incident_type = incident_type
        self.severity = severity
        self.description = description
        self.employee_id = employee_id
        self.location = location
        self.incident_date = incident_date or datetime.now()
        self.status = status

# Mock data
mock_violations = [
    ComplianceViolation(1, "I-9 Verification", "Missing I-9 form for new hire", "high", 5, "HR", "open", datetime.now() - timedelta(days=3), datetime.now() + timedelta(days=2)),
    ComplianceViolation(2, "Safety Training", "Overdue safety certification", "critical", 3, "Manufacturing", "open", datetime.now() - timedelta(days=5), datetime.now() - timedelta(days=1)),
    ComplianceViolation(3, "Overtime", "Excessive overtime without approval", "medium", 8, "Operations", "investigating", datetime.now() - timedelta(days=1))
]

mock_training = [
    ComplianceTraining(1, "Sexual Harassment Prevention", "All Employees", 91, datetime.now() + timedelta(days=90), "legal"),
    ComplianceTraining(2, "Safety Training", "Manufacturing", 88, datetime.now() + timedelta(days=15), "safety"),
    ComplianceTraining(3, "Data Privacy (GDPR)", "IT Department", 100, datetime.now() + timedelta(days=60), "privacy")
]

mock_incidents = [
    SafetyIncident(1, "Slip & Fall", "minor", "Employee slipped on wet floor", 10, "Warehouse", datetime.now() - timedelta(days=1), "investigating"),
    SafetyIncident(2, "Equipment Malfunction", "major", "Conveyor belt malfunction", 12, "Production Floor", datetime.now() - timedelta(days=4), "resolved"),
    SafetyIncident(3, "Chemical Exposure", "minor", "Minor exposure to cleaning chemicals", 15, "Maintenance", datetime.now() - timedelta(days=7), "closed")
]

@compliance.route('/api/compliance/dashboard', methods=['GET'])
@jwt_required()
def get_compliance_dashboard():
    """Get compliance dashboard overview"""
    try:
        # Calculate metrics
        total_violations = len(mock_violations)
        open_violations = len([v for v in mock_violations if v.status == "open"])
        critical_violations = len([v for v in mock_violations if v.severity == "critical"])
        
        # Training metrics
        avg_completion = sum(t.completion_rate for t in mock_training) / len(mock_training)
        overdue_training = len([t for t in mock_training if t.due_date < datetime.now()])
        
        # Safety metrics
        recent_incidents = len([i for i in mock_incidents if i.incident_date > datetime.now() - timedelta(days=30)])
        days_accident_free = (datetime.now() - max(i.incident_date for i in mock_incidents if i.severity in ["major", "critical"])).days
        
        return jsonify({
            'overall_score': 94,
            'violations': {
                'total': total_violations,
                'open': open_violations,
                'critical': critical_violations
            },
            'training': {
                'average_completion': round(avg_completion, 1),
                'overdue_count': overdue_training,
                'pending_employees': 12
            },
            'safety': {
                'recent_incidents': recent_incidents,
                'days_accident_free': days_accident_free,
                'osha_rate': 2.1
            },
            'audit_readiness': 87
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/violations', methods=['GET'])
@jwt_required()
def get_violations():
    """Get compliance violations"""
    try:
        status_filter = request.args.get('status')
        severity_filter = request.args.get('severity')
        
        filtered_violations = mock_violations
        
        if status_filter:
            filtered_violations = [v for v in filtered_violations if v.status == status_filter]
        
        if severity_filter:
            filtered_violations = [v for v in filtered_violations if v.severity == severity_filter]
        
        violations_data = []
        for violation in filtered_violations:
            violations_data.append({
                'id': violation.id,
                'type': violation.type,
                'description': violation.description,
                'severity': violation.severity,
                'employee_id': violation.employee_id,
                'department': violation.department,
                'status': violation.status,
                'created_date': violation.created_date.isoformat(),
                'due_date': violation.due_date.isoformat() if violation.due_date else None
            })
        
        return jsonify({
            'violations': violations_data,
            'total': len(violations_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/violations', methods=['POST'])
@jwt_required()
def create_violation():
    """Create a new compliance violation"""
    try:
        data = request.json
        
        required_fields = ['type', 'description', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_id = max([v.id for v in mock_violations]) + 1
        new_violation = ComplianceViolation(
            id=new_id,
            type=data['type'],
            description=data['description'],
            severity=data['severity'],
            employee_id=data.get('employee_id'),
            department=data.get('department'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d') if data.get('due_date') else None
        )
        
        mock_violations.append(new_violation)
        
        return jsonify({
            'message': 'Violation created successfully',
            'violation': {
                'id': new_violation.id,
                'type': new_violation.type,
                'severity': new_violation.severity,
                'status': new_violation.status
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/training', methods=['GET'])
@jwt_required()
def get_training_compliance():
    """Get training compliance status"""
    try:
        training_data = []
        for training in mock_training:
            training_data.append({
                'id': training.id,
                'name': training.name,
                'required_for': training.required_for,
                'completion_rate': training.completion_rate,
                'due_date': training.due_date.isoformat(),
                'category': training.category,
                'is_overdue': training.due_date < datetime.now(),
                'completed_count': int(156 * training.completion_rate / 100),
                'pending_count': 156 - int(156 * training.completion_rate / 100)
            })
        
        return jsonify({
            'training_programs': training_data,
            'summary': {
                'total_programs': len(mock_training),
                'overdue_programs': len([t for t in mock_training if t.due_date < datetime.now()]),
                'average_completion': sum(t.completion_rate for t in mock_training) / len(mock_training)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/safety/incidents', methods=['GET'])
@jwt_required()
def get_safety_incidents():
    """Get safety incidents"""
    try:
        incidents_data = []
        for incident in mock_incidents:
            incidents_data.append({
                'id': incident.id,
                'incident_type': incident.incident_type,
                'severity': incident.severity,
                'description': incident.description,
                'employee_id': incident.employee_id,
                'location': incident.location,
                'incident_date': incident.incident_date.isoformat(),
                'status': incident.status
            })
        
        return jsonify({
            'incidents': incidents_data,
            'total': len(incidents_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/safety/incidents', methods=['POST'])
@jwt_required()
def report_safety_incident():
    """Report a new safety incident"""
    try:
        data = request.json
        
        required_fields = ['incident_type', 'severity', 'description', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_id = max([i.id for i in mock_incidents]) + 1
        new_incident = SafetyIncident(
            id=new_id,
            incident_type=data['incident_type'],
            severity=data['severity'],
            description=data['description'],
            employee_id=data.get('employee_id'),
            location=data['location'],
            incident_date=datetime.strptime(data['incident_date'], '%Y-%m-%d') if data.get('incident_date') else datetime.now()
        )
        
        mock_incidents.append(new_incident)
        
        return jsonify({
            'message': 'Incident reported successfully',
            'incident': {
                'id': new_incident.id,
                'incident_type': new_incident.incident_type,
                'severity': new_incident.severity,
                'status': new_incident.status
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/reports/eeo', methods=['GET'])
@jwt_required()
def get_eeo_report():
    """Generate EEO-1 report data"""
    try:
        # Mock EEO data
        eeo_data = {
            'reporting_year': 2024,
            'company_info': {
                'name': 'Acme Corporation',
                'address': '123 Business St, City, State',
                'naics_code': '541511'
            },
            'workforce_data': {
                'executive_senior': {'male': 8, 'female': 4, 'total': 12},
                'mid_level': {'male': 45, 'female': 38, 'total': 83},
                'entry_level': {'male': 32, 'female': 28, 'total': 60},
                'total': {'male': 85, 'female': 70, 'total': 155}
            },
            'ethnicity_breakdown': {
                'white': 89,
                'black_african_american': 23,
                'hispanic_latino': 18,
                'asian': 15,
                'american_indian': 3,
                'pacific_islander': 2,
                'two_or_more': 5
            }
        }
        
        return jsonify({
            'success': True,
            'eeo_report': eeo_data,
            'generated_date': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/reports/osha', methods=['GET'])
@jwt_required()
def get_osha_report():
    """Generate OSHA 300 log data"""
    try:
        # Mock OSHA data
        osha_data = {
            'establishment_info': {
                'company_name': 'Acme Corporation',
                'establishment_name': 'Main Facility',
                'address': '123 Business St, City, State',
                'industry': 'Manufacturing'
            },
            'annual_summary': {
                'total_cases': 3,
                'days_away_from_work': 2,
                'job_transfer_restriction': 1,
                'total_recordable_cases': 3,
                'total_hours_worked': 320000,
                'osha_rate': 2.1
            },
            'incidents': [
                {
                    'case_no': 1,
                    'employee_name': 'Employee A',
                    'date_of_injury': '2024-09-28',
                    'description': 'Equipment malfunction injury',
                    'classification': 'Days away from work'
                },
                {
                    'case_no': 2,
                    'employee_name': 'Employee B',
                    'date_of_injury': '2024-10-01',
                    'description': 'Slip and fall',
                    'classification': 'Medical treatment'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'osha_report': osha_data,
            'generated_date': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/audit', methods=['GET'])
@jwt_required()
def get_audit_readiness():
    """Get audit readiness assessment"""
    try:
        audit_data = {
            'overall_score': 87,
            'areas': {
                'documentation': {'score': 92, 'status': 'good'},
                'policy_compliance': {'score': 85, 'status': 'good'},
                'training_records': {'score': 89, 'status': 'good'},
                'incident_reporting': {'score': 78, 'status': 'needs_improvement'},
                'record_keeping': {'score': 91, 'status': 'good'}
            },
            'recommendations': [
                'Update incident reporting procedures',
                'Complete outstanding I-9 verifications',
                'Implement automated compliance monitoring',
                'Schedule quarterly compliance reviews'
            ],
            'last_audit_date': '2024-01-15',
            'next_audit_due': '2025-01-15'
        }
        
        return jsonify({
            'success': True,
            'audit_readiness': audit_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compliance.route('/api/compliance/reminders', methods=['POST'])
@jwt_required()
def send_compliance_reminders():
    """Send compliance reminders"""
    try:
        data = request.json
        reminder_type = data.get('type', 'training')
        
        # Mock sending reminders
        sent_count = 0
        
        if reminder_type == 'training':
            # Send training reminders
            sent_count = 18  # Mock count
        elif reminder_type == 'violations':
            # Send violation reminders
            sent_count = 5
        elif reminder_type == 'certifications':
            # Send certification reminders
            sent_count = 12
        
        return jsonify({
            'success': True,
            'message': f'{sent_count} {reminder_type} reminders sent successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500