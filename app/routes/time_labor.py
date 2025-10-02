from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
import calendar

time_labor_bp = Blueprint('time_labor', __name__)

@time_labor_bp.route('/time-labor')
def time_labor():
    """Enhanced Time & Labor Management dashboard"""
    return render_template('time_labor.html')

@time_labor_bp.route('/api/time-labor/dashboard', methods=['GET'])
def get_time_labor_dashboard():
    """Get Time & Labor dashboard statistics"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'total_employees_clocked_in': 145,
                'employees_on_break': 12,
                'overtime_hours_today': 23.5,
                'attendance_rate_today': 94.2,
                'pending_timesheet_approvals': 8,
                'total_hours_worked_today': 1160,
                'avg_hours_per_employee': 8.2,
                'late_arrivals_today': 7
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@time_labor_bp.route('/api/time-labor/attendance', methods=['GET'])
def get_attendance():
    """Get daily attendance data"""
    try:
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        department = request.args.get('department', 'all')
        status_filter = request.args.get('status', 'all')
        
        # Mock attendance data
        attendance_data = [
            {
                'id': 1,
                'employee_id': 'EMP001',
                'employee_name': 'John Smith',
                'department': 'Information Technology',
                'position': 'Senior Developer',
                'scheduled_in': '09:00:00',
                'actual_in': '08:58:30',
                'scheduled_out': '18:00:00',
                'actual_out': '18:15:45',
                'break_duration': 60,
                'hours_worked': 9.25,
                'overtime_hours': 0.25,
                'status': 'present',
                'location': 'Office - Floor 3',
                'notes': 'Stayed late for deployment'
            },
            {
                'id': 2,
                'employee_id': 'EMP002',
                'employee_name': 'Sarah Johnson',
                'department': 'Marketing',
                'position': 'Marketing Manager',
                'scheduled_in': '09:00:00',
                'actual_in': '09:15:20',
                'scheduled_out': '18:00:00',
                'actual_out': None,
                'break_duration': 45,
                'hours_worked': 7.25,
                'overtime_hours': 0,
                'status': 'late',
                'location': 'Office - Floor 2',
                'notes': 'Traffic delay'
            },
            {
                'id': 3,
                'employee_id': 'EMP003',
                'employee_name': 'Mike Davis',
                'department': 'Finance',
                'position': 'Financial Analyst',
                'scheduled_in': '08:30:00',
                'actual_in': None,
                'scheduled_out': '17:30:00',
                'actual_out': None,
                'break_duration': 0,
                'hours_worked': 0,
                'overtime_hours': 0,
                'status': 'absent',
                'location': None,
                'notes': 'Sick leave'
            },
            {
                'id': 4,
                'employee_id': 'EMP004',
                'employee_name': 'Lisa Chen',
                'department': 'Human Resources',
                'position': 'HR Specialist',
                'scheduled_in': '09:00:00',
                'actual_in': '08:55:10',
                'scheduled_out': '18:00:00',
                'actual_out': '16:30:15',
                'break_duration': 60,
                'hours_worked': 7.5,
                'overtime_hours': 0,
                'status': 'early_leave',
                'location': 'Office - Floor 1',
                'notes': 'Doctor appointment'
            },
            {
                'id': 5,
                'employee_id': 'EMP005',
                'employee_name': 'Tom Wilson',
                'department': 'Operations',
                'position': 'Operations Manager',
                'scheduled_in': '08:00:00',
                'actual_in': '07:45:30',
                'scheduled_out': '17:00:00',
                'actual_out': '20:30:00',
                'break_duration': 75,
                'hours_worked': 12.5,
                'overtime_hours': 4.5,
                'status': 'overtime',
                'location': 'Office - Floor 4',
                'notes': 'Emergency system maintenance'
            }
        ]
        
        # Apply filters
        if department != 'all':
            attendance_data = [emp for emp in attendance_data if emp['department'].lower() == department.lower()]
        
        if status_filter != 'all':
            attendance_data = [emp for emp in attendance_data if emp['status'] == status_filter]
        
        return jsonify({
            'success': True,
            'data': attendance_data,
            'summary': {
                'total_employees': len(attendance_data),
                'present': len([emp for emp in attendance_data if emp['status'] == 'present']),
                'late': len([emp for emp in attendance_data if emp['status'] == 'late']),
                'absent': len([emp for emp in attendance_data if emp['status'] == 'absent']),
                'early_leave': len([emp for emp in attendance_data if emp['status'] == 'early_leave']),
                'overtime': len([emp for emp in attendance_data if emp['status'] == 'overtime'])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/clock', methods=['POST'])
def clock_action():
    """Handle clock in/out actions"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        action = data.get('action')  # 'in' or 'out'
        location = data.get('location', 'Office')
        notes = data.get('notes', '')
        
        current_time = datetime.now()
        
        # Mock clock action
        clock_record = {
            'id': f"CLK{current_time.strftime('%Y%m%d%H%M%S')}",
            'employee_id': employee_id,
            'action': action,
            'timestamp': current_time.isoformat(),
            'location': location,
            'notes': notes,
            'status': 'success'
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully clocked {action}',
            'data': clock_record
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/schedules', methods=['GET'])
def get_schedules():
    """Get employee work schedules"""
    try:
        employee_id = request.args.get('employee_id')
        week_start = request.args.get('week_start', datetime.now().strftime('%Y-%m-%d'))
        
        # Mock schedule data
        schedules = [
            {
                'id': 1,
                'employee_id': 'EMP001',
                'employee_name': 'John Smith',
                'shift_pattern': 'Standard',
                'monday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'tuesday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'wednesday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'thursday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'friday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'saturday': None,
                'sunday': None,
                'weekly_hours': 40,
                'overtime_eligible': True
            },
            {
                'id': 2,
                'employee_id': 'EMP002',
                'employee_name': 'Sarah Johnson',
                'shift_pattern': 'Flexible',
                'monday': {'start': '08:30', 'end': '17:30', 'break': 60},
                'tuesday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'wednesday': {'start': '10:00', 'end': '19:00', 'break': 60},
                'thursday': {'start': '09:00', 'end': '18:00', 'break': 60},
                'friday': {'start': '08:00', 'end': '17:00', 'break': 60},
                'saturday': None,
                'sunday': None,
                'weekly_hours': 40,
                'overtime_eligible': True
            },
            {
                'id': 3,
                'employee_id': 'EMP003',
                'employee_name': 'Mike Davis',
                'shift_pattern': 'Early Bird',
                'monday': {'start': '07:00', 'end': '16:00', 'break': 60},
                'tuesday': {'start': '07:00', 'end': '16:00', 'break': 60},
                'wednesday': {'start': '07:00', 'end': '16:00', 'break': 60},
                'thursday': {'start': '07:00', 'end': '16:00', 'break': 60},
                'friday': {'start': '07:00', 'end': '16:00', 'break': 60},
                'saturday': None,
                'sunday': None,
                'weekly_hours': 40,
                'overtime_eligible': True
            }
        ]
        
        if employee_id:
            schedules = [schedule for schedule in schedules if schedule['employee_id'] == employee_id]
        
        return jsonify({
            'success': True,
            'data': schedules
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/schedules', methods=['POST'])
def create_schedule():
    """Create new work schedule"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'shift_pattern', 'weekly_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        schedule = {
            'id': len(data) + 1,  # Mock ID generation
            'employee_id': data['employee_id'],
            'employee_name': data.get('employee_name'),
            'shift_pattern': data['shift_pattern'],
            'monday': data.get('monday'),
            'tuesday': data.get('tuesday'),
            'wednesday': data.get('wednesday'),
            'thursday': data.get('thursday'),
            'friday': data.get('friday'),
            'saturday': data.get('saturday'),
            'sunday': data.get('sunday'),
            'weekly_hours': data['weekly_hours'],
            'overtime_eligible': data.get('overtime_eligible', True),
            'effective_date': data.get('effective_date', datetime.now().strftime('%Y-%m-%d')),
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Schedule created successfully',
            'data': schedule
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/timesheets', methods=['GET'])
def get_timesheets():
    """Get employee timesheets"""
    try:
        employee_id = request.args.get('employee_id')
        week_ending = request.args.get('week_ending')
        status = request.args.get('status')
        
        # Mock timesheet data
        timesheets = [
            {
                'id': 1,
                'employee_id': 'EMP001',
                'employee_name': 'John Smith',
                'week_ending': '2025-10-06',
                'regular_hours': 40.0,
                'overtime_hours': 4.5,
                'double_time_hours': 0,
                'total_hours': 44.5,
                'status': 'submitted',
                'submitted_date': '2025-10-05',
                'approved_date': None,
                'approved_by': None,
                'daily_breakdown': [
                    {'date': '2025-09-30', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-01', 'hours': 9.5, 'overtime': 1.5},
                    {'date': '2025-10-02', 'hours': 9.0, 'overtime': 1.0},
                    {'date': '2025-10-03', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-04', 'hours': 10.0, 'overtime': 2.0}
                ]
            },
            {
                'id': 2,
                'employee_id': 'EMP002',
                'employee_name': 'Sarah Johnson',
                'week_ending': '2025-10-06',
                'regular_hours': 38.5,
                'overtime_hours': 0,
                'double_time_hours': 0,
                'total_hours': 38.5,
                'status': 'approved',
                'submitted_date': '2025-10-04',
                'approved_date': '2025-10-05',
                'approved_by': 'Manager',
                'daily_breakdown': [
                    {'date': '2025-09-30', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-01', 'hours': 7.5, 'overtime': 0},
                    {'date': '2025-10-02', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-03', 'hours': 7.0, 'overtime': 0},
                    {'date': '2025-10-04', 'hours': 8.0, 'overtime': 0}
                ]
            },
            {
                'id': 3,
                'employee_id': 'EMP003',
                'employee_name': 'Mike Davis',
                'week_ending': '2025-10-06',
                'regular_hours': 32.0,
                'overtime_hours': 0,
                'double_time_hours': 0,
                'total_hours': 32.0,
                'status': 'draft',
                'submitted_date': None,
                'approved_date': None,
                'approved_by': None,
                'daily_breakdown': [
                    {'date': '2025-09-30', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-01', 'hours': 0, 'overtime': 0},  # Sick day
                    {'date': '2025-10-02', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-03', 'hours': 8.0, 'overtime': 0},
                    {'date': '2025-10-04', 'hours': 8.0, 'overtime': 0}
                ]
            }
        ]
        
        # Apply filters
        if employee_id:
            timesheets = [ts for ts in timesheets if ts['employee_id'] == employee_id]
        
        if week_ending:
            timesheets = [ts for ts in timesheets if ts['week_ending'] == week_ending]
        
        if status:
            timesheets = [ts for ts in timesheets if ts['status'] == status]
        
        return jsonify({
            'success': True,
            'data': timesheets
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/timesheets/<int:timesheet_id>/approve', methods=['POST'])
def approve_timesheet(timesheet_id):
    """Approve a timesheet"""
    try:
        data = request.get_json()
        approver = data.get('approver', 'System')
        notes = data.get('notes', '')
        
        # Mock approval process
        approval_record = {
            'timesheet_id': timesheet_id,
            'approved_by': approver,
            'approved_date': datetime.now().isoformat(),
            'notes': notes,
            'status': 'approved'
        }
        
        return jsonify({
            'success': True,
            'message': 'Timesheet approved successfully',
            'data': approval_record
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/overtime', methods=['GET'])
def get_overtime():
    """Get overtime records"""
    try:
        employee_id = request.args.get('employee_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')
        
        # Mock overtime data
        overtime_records = [
            {
                'id': 1,
                'employee_id': 'EMP001',
                'employee_name': 'John Smith',
                'date': '2025-10-01',
                'regular_hours': 8.0,
                'overtime_hours': 2.5,
                'double_time_hours': 0,
                'reason': 'Project deadline - Q4 system upgrade',
                'pre_approved': True,
                'approved_by': 'IT Manager',
                'approval_date': '2025-09-30',
                'status': 'approved',
                'hourly_rate': 35.00,
                'overtime_rate': 52.50,
                'total_cost': 131.25
            },
            {
                'id': 2,
                'employee_id': 'EMP005',
                'employee_name': 'Tom Wilson',
                'date': '2025-10-02',
                'regular_hours': 8.0,
                'overtime_hours': 4.5,
                'double_time_hours': 0,
                'reason': 'Emergency system maintenance',
                'pre_approved': False,
                'approved_by': None,
                'approval_date': None,
                'status': 'pending',
                'hourly_rate': 45.00,
                'overtime_rate': 67.50,
                'total_cost': 303.75
            },
            {
                'id': 3,
                'employee_id': 'EMP002',
                'employee_name': 'Sarah Johnson',
                'date': '2025-09-29',
                'regular_hours': 8.0,
                'overtime_hours': 1.0,
                'double_time_hours': 0,
                'reason': 'Campaign launch preparation',
                'pre_approved': True,
                'approved_by': 'Marketing Director',
                'approval_date': '2025-09-28',
                'status': 'approved',
                'hourly_rate': 32.00,
                'overtime_rate': 48.00,
                'total_cost': 48.00
            }
        ]
        
        # Apply filters
        if employee_id:
            overtime_records = [ot for ot in overtime_records if ot['employee_id'] == employee_id]
        
        if status:
            overtime_records = [ot for ot in overtime_records if ot['status'] == status]
        
        return jsonify({
            'success': True,
            'data': overtime_records,
            'summary': {
                'total_records': len(overtime_records),
                'total_overtime_hours': sum(ot['overtime_hours'] for ot in overtime_records),
                'total_cost': sum(ot['total_cost'] for ot in overtime_records),
                'approved': len([ot for ot in overtime_records if ot['status'] == 'approved']),
                'pending': len([ot for ot in overtime_records if ot['status'] == 'pending']),
                'rejected': len([ot for ot in overtime_records if ot['status'] == 'rejected'])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/overtime/approve/<int:overtime_id>', methods=['POST'])
def approve_overtime(overtime_id):
    """Approve overtime request"""
    try:
        data = request.get_json()
        approver = data.get('approver', 'System')
        notes = data.get('notes', '')
        
        # Mock approval process
        approval_record = {
            'overtime_id': overtime_id,
            'approved_by': approver,
            'approved_date': datetime.now().isoformat(),
            'notes': notes,
            'status': 'approved'
        }
        
        return jsonify({
            'success': True,
            'message': 'Overtime approved successfully',
            'data': approval_record
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/analytics', methods=['GET'])
def get_labor_analytics():
    """Get labor analytics and insights"""
    try:
        period = request.args.get('period', 'week')  # week, month, quarter, year
        department = request.args.get('department', 'all')
        
        # Mock analytics data
        analytics = {
            'attendance_metrics': {
                'average_attendance_rate': 94.5,
                'punctuality_rate': 87.2,
                'early_departure_rate': 3.1,
                'overtime_rate': 12.3,
                'trend': '+2.1% from last period'
            },
            'productivity_insights': {
                'hours_per_employee_avg': 41.2,
                'productivity_score': 89.4,
                'efficiency_rating': 'High',
                'cost_per_hour': 47.50,
                'trend': '+1.8% productivity increase'
            },
            'time_distribution': {
                'regular_hours': 85.2,
                'overtime_hours': 12.3,
                'break_time': 2.5,
                'total_billable': 97.5
            },
            'department_breakdown': [
                {'name': 'IT', 'hours': 320, 'overtime': 32, 'cost': 15200},
                {'name': 'Marketing', 'hours': 280, 'overtime': 18, 'cost': 11200},
                {'name': 'Finance', 'hours': 240, 'overtime': 12, 'cost': 10800},
                {'name': 'Operations', 'hours': 360, 'overtime': 24, 'cost': 14400}
            ],
            'cost_analysis': {
                'total_labor_cost': 51600,
                'overtime_cost': 8640,
                'cost_per_employee': 516,
                'budget_variance': -2.3,
                'savings_opportunities': 2500
            },
            'trends': {
                'weekly_hours': [38.5, 39.2, 41.1, 40.8, 41.2],
                'attendance_rates': [93.2, 94.1, 94.5, 93.8, 94.5],
                'overtime_trends': [10.2, 11.5, 12.3, 11.8, 12.3]
            }
        }
        
        return jsonify({
            'success': True,
            'data': analytics,
            'period': period,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@time_labor_bp.route('/api/time-labor/reports/generate', methods=['POST'])
def generate_report():
    """Generate time and labor reports"""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'attendance')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        employees = data.get('employees', [])
        departments = data.get('departments', [])
        
        # Mock report generation
        report = {
            'id': f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': report_type,
            'title': f"{report_type.title()} Report",
            'period': f"{date_from} to {date_to}",
            'generated_by': 'System',
            'generated_at': datetime.now().isoformat(),
            'status': 'ready',
            'file_url': f"/reports/time-labor/{report_type}-{datetime.now().strftime('%Y%m%d')}.pdf",
            'summary': {
                'total_records': 150,
                'total_employees': 15,
                'total_hours': 1200,
                'total_overtime': 84
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'data': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500