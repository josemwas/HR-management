from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

self_service = Blueprint('self_service', __name__)

# Mock Employee Self-Service Request class
class EmployeeRequest:
    def __init__(self, id, employee_id, employee_name, request_type, description, status="pending", created_date=None, start_date=None, end_date=None):
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.request_type = request_type
        self.description = description
        self.status = status
        self.created_date = created_date or datetime.now()
        self.start_date = start_date
        self.end_date = end_date

# Mock data
mock_employee_requests = [
    EmployeeRequest(1, 1, "John Smith", "leave", "Vacation request", "pending", datetime.now() - timedelta(days=2), "2024-10-15", "2024-10-17"),
    EmployeeRequest(2, 1, "John Smith", "info_change", "Update phone number", "approved", datetime.now() - timedelta(days=5)),
    EmployeeRequest(3, 2, "Jane Doe", "document", "Request employment letter", "completed", datetime.now() - timedelta(days=7)),
]

mock_pay_stubs = [
    {
        'period': 'September 2024',
        'gross_pay': 5500.00,
        'deductions': 825.00,
        'net_pay': 4675.00,
        'pay_date': '2024-09-30'
    },
    {
        'period': 'August 2024',
        'gross_pay': 5500.00,
        'deductions': 825.00,
        'net_pay': 4675.00,
        'pay_date': '2024-08-31'
    },
    {
        'period': 'July 2024',
        'gross_pay': 5500.00,
        'deductions': 825.00,
        'net_pay': 4675.00,
        'pay_date': '2024-07-31'
    }
]

mock_documents = [
    {
        'id': 1,
        'name': 'Employment Contract',
        'type': 'Contract',
        'upload_date': '2023-01-15',
        'file_path': '/documents/contract_001.pdf'
    },
    {
        'id': 2,
        'name': 'Tax Forms (W-2)',
        'type': 'Tax',
        'upload_date': '2024-01-31',
        'file_path': '/documents/w2_2023.pdf'
    },
    {
        'id': 3,
        'name': 'Benefits Enrollment',
        'type': 'Benefits',
        'upload_date': '2023-01-20',
        'file_path': '/documents/benefits_enrollment.pdf'
    }
]

@self_service.route('/api/self-service/profile', methods=['GET'])
@jwt_required()
def get_employee_profile():
    """Get employee profile information"""
    try:
        current_user = get_jwt_identity()
        
        # In real implementation, fetch from database
        profile_data = {
            'employee_id': int(current_user),
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@company.com',
            'phone': '+1-555-0123',
            'address': '123 Main St, City, State 12345',
            'emergency_contact_name': 'Jane Smith',
            'emergency_contact_phone': '+1-555-0124',
            'department': 'Engineering',
            'position': 'Software Engineer',
            'hire_date': '2023-01-15',
            'employment_status': 'Active',
            'salary': 66000.00,
            'manager': 'Sarah Johnson'
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/profile', methods=['PUT'])
@jwt_required()
def update_employee_profile():
    """Update employee profile information"""
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        # Validate updateable fields
        allowed_fields = ['phone', 'address', 'emergency_contact_name', 'emergency_contact_phone']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # In real implementation, update database
        print(f"Updating profile for user {current_user}: {update_data}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'updated_fields': list(update_data.keys())
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/requests', methods=['GET'])
@jwt_required()
def get_employee_requests():
    """Get employee's requests"""
    try:
        current_user = get_jwt_identity()
        
        # Filter requests for current user
        user_requests = [req for req in mock_employee_requests if req.employee_id == int(current_user)]
        
        requests_data = []
        for req in user_requests:
            requests_data.append({
                'id': req.id,
                'type': req.request_type,
                'description': req.description,
                'status': req.status,
                'created_date': req.created_date.isoformat(),
                'start_date': req.start_date,
                'end_date': req.end_date
            })
        
        return jsonify({
            'success': True,
            'requests': requests_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/requests', methods=['POST'])
@jwt_required()
def create_employee_request():
    """Create a new employee request"""
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        required_fields = ['type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new request
        new_id = max([req.id for req in mock_employee_requests]) + 1
        new_request = EmployeeRequest(
            id=new_id,
            employee_id=int(current_user),
            employee_name="Current User",  # In real app, get from user data
            request_type=data['type'],
            description=data['description'],
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        mock_employee_requests.append(new_request)
        
        return jsonify({
            'success': True,
            'message': 'Request submitted successfully',
            'request': {
                'id': new_request.id,
                'type': new_request.request_type,
                'status': new_request.status,
                'created_date': new_request.created_date.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/pay-stubs', methods=['GET'])
@jwt_required()
def get_pay_stubs():
    """Get employee pay stubs"""
    try:
        current_user = get_jwt_identity()
        
        # In real implementation, filter by employee ID
        return jsonify({
            'success': True,
            'pay_stubs': mock_pay_stubs
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/pay-stubs/<period>/download', methods=['GET'])
@jwt_required()
def download_pay_stub(period):
    """Download pay stub PDF"""
    try:
        current_user = get_jwt_identity()
        
        # In real implementation, generate and serve PDF
        return jsonify({
            'success': True,
            'message': f'Pay stub for {period} would be downloaded',
            'download_url': f'/downloads/paystub_{period.replace(" ", "_").lower()}.pdf'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/documents', methods=['GET'])
@jwt_required()
def get_employee_documents():
    """Get employee documents"""
    try:
        current_user = get_jwt_identity()
        
        # In real implementation, filter by employee ID and access permissions
        return jsonify({
            'success': True,
            'documents': mock_documents
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/documents/<int:document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download employee document"""
    try:
        current_user = get_jwt_identity()
        
        document = next((doc for doc in mock_documents if doc['id'] == document_id), None)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # In real implementation, serve the actual file
        return jsonify({
            'success': True,
            'message': f'Document {document["name"]} would be downloaded',
            'download_url': document['file_path']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/benefits', methods=['GET'])
@jwt_required()
def get_employee_benefits():
    """Get employee benefits information"""
    try:
        current_user = get_jwt_identity()
        
        benefits_data = {
            'health_insurance': {
                'plan': 'Premium Plan',
                'employee_contribution': 20,
                'company_contribution': 80,
                'coverage': ['Medical', 'Dental', 'Vision'],
                'annual_premium': 12000,
                'employee_cost': 2400
            },
            'retirement_401k': {
                'employee_contribution_percent': 6,
                'company_match_percent': 3,
                'current_balance': 12500,
                'ytd_contributions': 3300,
                'company_match': 1650
            },
            'paid_time_off': {
                'annual_accrual': 15,
                'used_days': 5,
                'available_days': 10,
                'accrual_rate': 1.25,
                'carryover_limit': 5
            },
            'training_budget': {
                'annual_budget': 2000,
                'used_amount': 800,
                'remaining_amount': 1200,
                'courses_completed': 3
            },
            'other_benefits': [
                'Life Insurance ($50,000)',
                'Disability Insurance',
                'Flexible Spending Account',
                'Employee Assistance Program',
                'Gym Membership Reimbursement'
            ]
        }
        
        return jsonify({
            'success': True,
            'benefits': benefits_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/time-off-balance', methods=['GET'])
@jwt_required()
def get_time_off_balance():
    """Get employee time off balance"""
    try:
        current_user = get_jwt_identity()
        
        balance_data = {
            'vacation': {
                'available': 10,
                'used': 5,
                'accrued': 15,
                'pending': 2
            },
            'sick': {
                'available': 8,
                'used': 2,
                'accrued': 10,
                'pending': 0
            },
            'personal': {
                'available': 3,
                'used': 0,
                'accrued': 3,
                'pending': 0
            }
        }
        
        return jsonify({
            'success': True,
            'time_off_balance': balance_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change employee password"""
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate password strength
        new_password = data['new_password']
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # In real implementation, verify current password and update
        print(f"Password change request for user {current_user}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@self_service.route('/api/self-service/emergency-contact', methods=['PUT'])
@jwt_required()
def update_emergency_contact():
    """Update emergency contact information"""
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        required_fields = ['name', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In real implementation, update in database
        update_data = {
            'emergency_contact_name': data['name'],
            'emergency_contact_phone': data['phone'],
            'emergency_contact_relationship': data.get('relationship', ''),
            'emergency_contact_address': data.get('address', '')
        }
        
        print(f"Updating emergency contact for user {current_user}: {update_data}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact updated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500