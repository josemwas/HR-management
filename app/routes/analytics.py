from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

analytics = Blueprint('analytics', __name__)

# Mock analytics data generator
class AnalyticsService:
    @staticmethod
    def get_employee_metrics():
        return {
            'total_employees': 156,
            'active_employees': 148,
            'new_hires_this_month': 8,
            'turnover_rate': 2.3,
            'avg_tenure_months': 28.5,
            'employee_satisfaction': 8.2
        }
    
    @staticmethod
    def get_attendance_metrics():
        return {
            'attendance_rate': 94.5,
            'punctuality_rate': 87.3,
            'avg_hours_per_week': 42.1,
            'overtime_hours': 156.8,
            'remote_work_percentage': 35.2,
            'sick_leave_usage': 3.2
        }
    
    @staticmethod
    def get_performance_metrics():
        return {
            'avg_performance_score': 7.8,
            'goals_completion_rate': 82.1,
            'training_completion_rate': 76.9,
            'promotion_rate': 12.5,
            'high_performers_percentage': 18.3,
            'improvement_needed_percentage': 8.7
        }
    
    @staticmethod
    def get_financial_metrics():
        return {
            'total_payroll': 2890450.75,
            'avg_salary': 68750.25,
            'benefits_cost': 437500.50,
            'recruitment_cost': 89250.00,
            'training_cost': 45600.75,
            'cost_per_employee': 2150.35
        }
    
    @staticmethod
    def get_department_breakdown():
        return {
            'Engineering': {'count': 45, 'avg_salary': 85000, 'satisfaction': 8.5},
            'Sales': {'count': 28, 'avg_salary': 65000, 'satisfaction': 7.8},
            'Marketing': {'count': 18, 'avg_salary': 62000, 'satisfaction': 8.1},
            'HR': {'count': 12, 'avg_salary': 58000, 'satisfaction': 8.3},
            'Finance': {'count': 15, 'avg_salary': 72000, 'satisfaction': 7.9},
            'Operations': {'count': 22, 'avg_salary': 55000, 'satisfaction': 7.6},
            'Customer Support': {'count': 16, 'avg_salary': 48000, 'satisfaction': 8.0}
        }
    
    @staticmethod
    def get_trend_data():
        # Mock 12 months of trend data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return {
            'employee_growth': [140, 142, 145, 148, 150, 152, 154, 156, 158, 156, 154, 156],
            'satisfaction_scores': [7.8, 7.9, 8.0, 8.1, 8.2, 8.0, 8.1, 8.2, 8.3, 8.2, 8.1, 8.2],
            'attendance_rates': [92.1, 93.2, 94.5, 95.1, 94.8, 93.9, 94.2, 94.5, 95.2, 94.7, 93.8, 94.5],
            'turnover_rates': [3.2, 2.8, 2.5, 2.1, 1.9, 2.2, 2.5, 2.3, 2.1, 2.0, 2.2, 2.3],
            'months': months
        }

@analytics.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get main dashboard analytics"""
    try:
        return jsonify({
            'employee_metrics': AnalyticsService.get_employee_metrics(),
            'attendance_metrics': AnalyticsService.get_attendance_metrics(),
            'performance_metrics': AnalyticsService.get_performance_metrics(),
            'financial_metrics': AnalyticsService.get_financial_metrics(),
            'last_updated': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/departments', methods=['GET'])
@jwt_required()
def get_department_analytics():
    """Get department-wise analytics"""
    try:
        department_data = AnalyticsService.get_department_breakdown()
        
        # Calculate totals and averages
        total_employees = sum(dept['count'] for dept in department_data.values())
        total_salary_cost = sum(dept['count'] * dept['avg_salary'] for dept in department_data.values())
        avg_satisfaction = sum(dept['satisfaction'] * dept['count'] for dept in department_data.values()) / total_employees
        
        return jsonify({
            'departments': department_data,
            'summary': {
                'total_employees': total_employees,
                'total_salary_cost': total_salary_cost,
                'avg_satisfaction': round(avg_satisfaction, 2),
                'department_count': len(department_data)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_trend_analytics():
    """Get historical trend data"""
    try:
        period = request.args.get('period', '12m')  # 3m, 6m, 12m
        
        trend_data = AnalyticsService.get_trend_data()
        
        if period == '3m':
            # Last 3 months
            for key in ['employee_growth', 'satisfaction_scores', 'attendance_rates', 'turnover_rates']:
                trend_data[key] = trend_data[key][-3:]
            trend_data['months'] = trend_data['months'][-3:]
        elif period == '6m':
            # Last 6 months
            for key in ['employee_growth', 'satisfaction_scores', 'attendance_rates', 'turnover_rates']:
                trend_data[key] = trend_data[key][-6:]
            trend_data['months'] = trend_data['months'][-6:]
        
        return jsonify(trend_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Get detailed performance analytics"""
    try:
        return jsonify({
            'overall_metrics': AnalyticsService.get_performance_metrics(),
            'performance_distribution': {
                'excellent': 18.3,
                'good': 45.7,
                'satisfactory': 27.3,
                'needs_improvement': 8.7
            },
            'goal_categories': {
                'Sales Targets': {'completion_rate': 87.5, 'avg_score': 8.2},
                'Project Delivery': {'completion_rate': 78.9, 'avg_score': 7.8},
                'Skill Development': {'completion_rate': 82.3, 'avg_score': 8.0},
                'Team Collaboration': {'completion_rate': 89.1, 'avg_score': 8.4},
                'Innovation': {'completion_rate': 72.6, 'avg_score': 7.5}
            },
            'training_effectiveness': {
                'technical_skills': 8.1,
                'soft_skills': 7.8,
                'leadership': 8.3,
                'compliance': 8.7
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/attendance', methods=['GET'])
@jwt_required()
def get_attendance_analytics():
    """Get detailed attendance analytics"""
    try:
        return jsonify({
            'overall_metrics': AnalyticsService.get_attendance_metrics(),
            'attendance_patterns': {
                'monday': 92.1,
                'tuesday': 94.8,
                'wednesday': 95.2,
                'thursday': 94.6,
                'friday': 91.3
            },
            'leave_analysis': {
                'sick_leave': {'total_days': 245, 'avg_per_employee': 1.6},
                'vacation': {'total_days': 892, 'avg_per_employee': 5.7},
                'personal': {'total_days': 156, 'avg_per_employee': 1.0},
                'maternity_paternity': {'total_days': 89, 'avg_per_employee': 0.6}
            },
            'punctuality_insights': {
                'on_time_percentage': 87.3,
                'late_5_to_15_min': 8.2,
                'late_15_to_30_min': 3.1,
                'late_over_30_min': 1.4
            },
            'remote_work_stats': {
                'full_remote': 15.2,
                'hybrid': 35.2,
                'office_only': 49.6
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/recruitment', methods=['GET'])
@jwt_required()
def get_recruitment_analytics():
    """Get recruitment and hiring analytics"""
    try:
        return jsonify({
            'hiring_metrics': {
                'positions_open': 12,
                'applications_received': 324,
                'interviews_conducted': 89,
                'offers_made': 15,
                'offers_accepted': 12,
                'time_to_hire_days': 28.5
            },
            'source_effectiveness': {
                'job_boards': {'applications': 156, 'hires': 5},
                'referrals': {'applications': 89, 'hires': 4},
                'social_media': {'applications': 45, 'hires': 2},
                'recruitment_agencies': {'applications': 34, 'hires': 1}
            },
            'position_demand': {
                'Software Engineer': 4,
                'Sales Representative': 3,
                'Marketing Specialist': 2,
                'Customer Support': 2,
                'Data Analyst': 1
            },
            'candidate_pipeline': {
                'application_review': 89,
                'phone_screening': 45,
                'technical_interview': 23,
                'final_interview': 15,
                'offer_stage': 8
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/financial', methods=['GET'])
@jwt_required()
def get_financial_analytics():
    """Get HR-related financial analytics"""
    try:
        return jsonify({
            'cost_breakdown': AnalyticsService.get_financial_metrics(),
            'salary_distribution': {
                'entry_level': {'range': '40-60k', 'count': 45, 'percentage': 28.8},
                'mid_level': {'range': '60-80k', 'count': 67, 'percentage': 42.9},
                'senior_level': {'range': '80-120k', 'count': 32, 'percentage': 20.5},
                'executive': {'range': '120k+', 'count': 12, 'percentage': 7.7}
            },
            'benefits_utilization': {
                'health_insurance': 94.2,
                'dental': 87.5,
                'vision': 78.3,
                'retirement_401k': 89.1,
                'life_insurance': 72.4,
                'disability': 65.8
            },
            'cost_per_hire': {
                'recruitment_advertising': 1250.00,
                'agency_fees': 2100.00,
                'internal_hr_time': 890.00,
                'interview_expenses': 340.00,
                'total': 4580.00
            },
            'roi_metrics': {
                'training_roi': 3.2,
                'employee_retention_savings': 125000.00,
                'productivity_improvement': 15.8
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/analytics/export', methods=['POST'])
@jwt_required()
def export_analytics():
    """Export analytics data"""
    try:
        data = request.json
        report_type = data.get('type', 'dashboard')
        format_type = data.get('format', 'json')  # json, csv, pdf
        
        # Generate export data based on type
        export_data = {}
        
        if report_type == 'dashboard':
            export_data = {
                'employee_metrics': AnalyticsService.get_employee_metrics(),
                'attendance_metrics': AnalyticsService.get_attendance_metrics(),
                'performance_metrics': AnalyticsService.get_performance_metrics(),
                'financial_metrics': AnalyticsService.get_financial_metrics()
            }
        elif report_type == 'departments':
            export_data = AnalyticsService.get_department_breakdown()
        elif report_type == 'trends':
            export_data = AnalyticsService.get_trend_data()
        
        # In a real application, you would generate the actual file here
        # For now, return the data structure
        
        return jsonify({
            'message': f'Analytics export generated successfully',
            'export_id': f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'type': report_type,
            'format': format_type,
            'data': export_data,
            'generated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500