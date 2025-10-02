from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

timesheets = Blueprint('timesheets', __name__)

# Mock Timesheet class for demonstration
class Timesheet:
    def __init__(self, id, employee_id, employee_name, date, clock_in, clock_out=None, break_start=None, break_end=None, total_hours=0, status="active"):
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.date = date
        self.clock_in = clock_in
        self.clock_out = clock_out
        self.break_start = break_start
        self.break_end = break_end
        self.total_hours = total_hours
        self.status = status

# Mock data
mock_timesheets = [
    Timesheet(1, 1, "John Smith", datetime.now().date(), datetime.now().replace(hour=9, minute=0), datetime.now().replace(hour=17, minute=30), datetime.now().replace(hour=12, minute=0), datetime.now().replace(hour=13, minute=0), 7.5, "completed"),
    Timesheet(2, 2, "Jane Doe", datetime.now().date(), datetime.now().replace(hour=8, minute=30), datetime.now().replace(hour=17, minute=0), datetime.now().replace(hour=12, minute=30), datetime.now().replace(hour=13, minute=30), 7.5, "completed"),
    Timesheet(3, 3, "Bob Wilson", datetime.now().date(), datetime.now().replace(hour=9, minute=15), None, None, None, 0, "active"),
    Timesheet(4, 1, "John Smith", datetime.now().date() - timedelta(days=1), datetime.now().replace(hour=9, minute=0), datetime.now().replace(hour=18, minute=0), datetime.now().replace(hour=12, minute=0), datetime.now().replace(hour=13, minute=0), 8.0, "completed"),
    Timesheet(5, 2, "Jane Doe", datetime.now().date() - timedelta(days=1), datetime.now().replace(hour=8, minute=45), datetime.now().replace(hour=17, minute=15), None, None, 8.5, "completed"),
]

@timesheets.route('/api/timesheets', methods=['GET'])
@jwt_required()
def get_timesheets():
    """Get timesheets with filtering"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')
        
        filtered_timesheets = mock_timesheets
        
        if employee_id:
            filtered_timesheets = [ts for ts in filtered_timesheets if ts.employee_id == employee_id]
        
        if status:
            filtered_timesheets = [ts for ts in filtered_timesheets if ts.status == status]
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            filtered_timesheets = [ts for ts in filtered_timesheets if ts.date >= date_from]
        
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            filtered_timesheets = [ts for ts in filtered_timesheets if ts.date <= date_to]
        
        timesheets_data = []
        for ts in filtered_timesheets:
            timesheets_data.append({
                'id': ts.id,
                'employee_id': ts.employee_id,
                'employee_name': ts.employee_name,
                'date': ts.date.isoformat(),
                'clock_in': ts.clock_in.strftime('%H:%M') if ts.clock_in else None,
                'clock_out': ts.clock_out.strftime('%H:%M') if ts.clock_out else None,
                'break_start': ts.break_start.strftime('%H:%M') if ts.break_start else None,
                'break_end': ts.break_end.strftime('%H:%M') if ts.break_end else None,
                'total_hours': ts.total_hours,
                'status': ts.status
            })
        
        return jsonify({
            'timesheets': timesheets_data,
            'total': len(timesheets_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/<int:timesheet_id>', methods=['GET'])
@jwt_required()
def get_timesheet(timesheet_id):
    """Get specific timesheet details"""
    try:
        timesheet = next((ts for ts in mock_timesheets if ts.id == timesheet_id), None)
        
        if not timesheet:
            return jsonify({'error': 'Timesheet not found'}), 404
        
        return jsonify({
            'id': timesheet.id,
            'employee_id': timesheet.employee_id,
            'employee_name': timesheet.employee_name,
            'date': timesheet.date.isoformat(),
            'clock_in': timesheet.clock_in.strftime('%H:%M') if timesheet.clock_in else None,
            'clock_out': timesheet.clock_out.strftime('%H:%M') if timesheet.clock_out else None,
            'break_start': timesheet.break_start.strftime('%H:%M') if timesheet.break_start else None,
            'break_end': timesheet.break_end.strftime('%H:%M') if timesheet.break_end else None,
            'total_hours': timesheet.total_hours,
            'status': timesheet.status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    """Clock in for the current day"""
    try:
        current_user = get_jwt_identity()
        today = datetime.now().date()
        
        # Check if already clocked in today
        existing = next((ts for ts in mock_timesheets if ts.employee_id == int(current_user) and ts.date == today), None)
        
        if existing:
            return jsonify({'error': 'Already clocked in today'}), 400
        
        # Create new timesheet entry
        new_id = max([ts.id for ts in mock_timesheets]) + 1
        new_timesheet = Timesheet(
            id=new_id,
            employee_id=int(current_user),
            employee_name="Current User",  # In real app, get from user data
            date=today,
            clock_in=datetime.now(),
            status="active"
        )
        
        mock_timesheets.append(new_timesheet)
        
        return jsonify({
            'message': 'Clocked in successfully',
            'timesheet': {
                'id': new_timesheet.id,
                'clock_in': new_timesheet.clock_in.strftime('%H:%M'),
                'date': new_timesheet.date.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/<int:timesheet_id>/clock-out', methods=['POST'])
@jwt_required()
def clock_out(timesheet_id):
    """Clock out for a timesheet"""
    try:
        timesheet = next((ts for ts in mock_timesheets if ts.id == timesheet_id), None)
        
        if not timesheet:
            return jsonify({'error': 'Timesheet not found'}), 404
        
        if timesheet.status != 'active':
            return jsonify({'error': 'Cannot clock out - timesheet not active'}), 400
        
        # Update timesheet
        timesheet.clock_out = datetime.now()
        timesheet.status = 'completed'
        
        # Calculate total hours (simplified calculation)
        if timesheet.clock_in and timesheet.clock_out:
            time_diff = timesheet.clock_out - timesheet.clock_in
            total_seconds = time_diff.total_seconds()
            
            # Subtract break time if exists
            if timesheet.break_start and timesheet.break_end:
                break_diff = timesheet.break_end - timesheet.break_start
                total_seconds -= break_diff.total_seconds()
            
            timesheet.total_hours = round(total_seconds / 3600, 2)
        
        return jsonify({
            'message': 'Clocked out successfully',
            'timesheet': {
                'id': timesheet.id,
                'clock_out': timesheet.clock_out.strftime('%H:%M'),
                'total_hours': timesheet.total_hours,
                'status': timesheet.status
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/<int:timesheet_id>/break', methods=['POST'])
@jwt_required()
def manage_break(timesheet_id):
    """Start or end break for a timesheet"""
    try:
        data = request.json
        action = data.get('action')  # 'start' or 'end'
        
        timesheet = next((ts for ts in mock_timesheets if ts.id == timesheet_id), None)
        
        if not timesheet:
            return jsonify({'error': 'Timesheet not found'}), 404
        
        if timesheet.status != 'active':
            return jsonify({'error': 'Cannot manage break - timesheet not active'}), 400
        
        if action == 'start':
            if timesheet.break_start:
                return jsonify({'error': 'Break already started'}), 400
            timesheet.break_start = datetime.now()
            message = 'Break started'
        
        elif action == 'end':
            if not timesheet.break_start:
                return jsonify({'error': 'Break not started yet'}), 400
            if timesheet.break_end:
                return jsonify({'error': 'Break already ended'}), 400
            timesheet.break_end = datetime.now()
            message = 'Break ended'
        
        else:
            return jsonify({'error': 'Invalid action. Use "start" or "end"'}), 400
        
        return jsonify({
            'message': message,
            'timesheet': {
                'id': timesheet.id,
                'break_start': timesheet.break_start.strftime('%H:%M') if timesheet.break_start else None,
                'break_end': timesheet.break_end.strftime('%H:%M') if timesheet.break_end else None
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get timesheet analytics"""
    try:
        # Weekly summary
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_timesheets = [ts for ts in mock_timesheets if ts.date >= week_start and ts.date <= today]
        
        # Calculate weekly totals
        total_hours_week = sum(ts.total_hours for ts in week_timesheets)
        avg_hours_per_day = round(total_hours_week / 7, 2) if week_timesheets else 0
        
        # Employee productivity
        employee_stats = {}
        for ts in mock_timesheets:
            if ts.employee_name not in employee_stats:
                employee_stats[ts.employee_name] = {'total_hours': 0, 'days_worked': 0}
            employee_stats[ts.employee_name]['total_hours'] += ts.total_hours
            if ts.status == 'completed':
                employee_stats[ts.employee_name]['days_worked'] += 1
        
        # Active sessions
        active_sessions = len([ts for ts in mock_timesheets if ts.status == 'active'])
        
        # Late arrivals (after 9:30 AM)
        late_arrivals = len([ts for ts in mock_timesheets if ts.clock_in and ts.clock_in.time() > datetime.strptime('09:30', '%H:%M').time()])
        
        return jsonify({
            'weekly_summary': {
                'total_hours': total_hours_week,
                'average_hours_per_day': avg_hours_per_day,
                'days_in_week': len(set(ts.date for ts in week_timesheets))
            },
            'employee_productivity': employee_stats,
            'current_status': {
                'active_sessions': active_sessions,
                'employees_working': len(set(ts.employee_id for ts in mock_timesheets if ts.status == 'active'))
            },
            'attendance_insights': {
                'late_arrivals_this_week': late_arrivals,
                'on_time_percentage': round((len(week_timesheets) - late_arrivals) / len(week_timesheets) * 100, 1) if week_timesheets else 100
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timesheets.route('/api/timesheets/current-status', methods=['GET'])
@jwt_required()
def get_current_status():
    """Get current timesheet status for logged-in user"""
    try:
        current_user = get_jwt_identity()
        today = datetime.now().date()
        
        # Find today's timesheet for current user
        current_timesheet = next((ts for ts in mock_timesheets if ts.employee_id == int(current_user) and ts.date == today), None)
        
        if not current_timesheet:
            return jsonify({
                'status': 'not_clocked_in',
                'message': 'Not clocked in today'
            })
        
        return jsonify({
            'status': current_timesheet.status,
            'timesheet': {
                'id': current_timesheet.id,
                'clock_in': current_timesheet.clock_in.strftime('%H:%M') if current_timesheet.clock_in else None,
                'clock_out': current_timesheet.clock_out.strftime('%H:%M') if current_timesheet.clock_out else None,
                'break_start': current_timesheet.break_start.strftime('%H:%M') if current_timesheet.break_start else None,
                'break_end': current_timesheet.break_end.strftime('%H:%M') if current_timesheet.break_end else None,
                'total_hours': current_timesheet.total_hours
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500