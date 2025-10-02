from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

compensation = Blueprint('compensation', __name__)

# Mock Compensation classes
class SalaryBand:
    def __init__(self, id, grade, title, min_salary, max_salary, midpoint, department=None, employee_count=0):
        self.id = id
        self.grade = grade
        self.title = title
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.midpoint = midpoint
        self.department = department
        self.employee_count = employee_count

class CompensationBenchmark:
    def __init__(self, position, our_avg, market_25th, market_50th, market_75th, source, last_updated):
        self.position = position
        self.our_avg = our_avg
        self.market_25th = market_25th
        self.market_50th = market_50th
        self.market_75th = market_75th
        self.source = source
        self.last_updated = last_updated

# Mock data
mock_salary_bands = [
    SalaryBand(1, "Grade 1", "Entry Level", 40000, 55000, 47500, "All", 28),
    SalaryBand(2, "Grade 2", "Junior", 50000, 68000, 59000, "All", 42),
    SalaryBand(3, "Grade 3", "Mid-Level", 65000, 85000, 75000, "All", 38),
    SalaryBand(4, "Grade 4", "Senior", 80000, 110000, 95000, "All", 25),
    SalaryBand(5, "Grade 5", "Lead/Principal", 105000, 140000, 122500, "All", 15),
    SalaryBand(6, "Grade 6", "Executive", 135000, 200000, 167500, "All", 8)
]

mock_benchmarks = [
    CompensationBenchmark("Software Engineer", 82500, 75000, 85000, 95000, "PayScale", datetime.now() - timedelta(days=30)),
    CompensationBenchmark("Sales Manager", 95000, 85000, 95000, 105000, "Glassdoor", datetime.now() - timedelta(days=45)),
    CompensationBenchmark("Data Analyst", 65000, 68000, 75000, 82000, "Salary.com", datetime.now() - timedelta(days=60)),
    CompensationBenchmark("HR Specialist", 58000, 52000, 58000, 65000, "Industry Survey", datetime.now() - timedelta(days=90))
]

@compensation.route('/api/compensation/overview', methods=['GET'])
@jwt_required()
def get_compensation_overview():
    """Get compensation overview dashboard"""
    try:
        # Calculate metrics
        total_employees = 156
        total_compensation = 10720000  # $10.72M
        avg_salary = total_compensation / total_employees
        
        # Department breakdown
        departments = {
            'Engineering': {'count': 45, 'avg_salary': 85000, 'min': 65000, 'max': 125000},
            'Sales': {'count': 28, 'avg_salary': 65000, 'min': 45000, 'max': 95000},
            'Marketing': {'count': 18, 'avg_salary': 62000, 'min': 48000, 'max': 85000},
            'Operations': {'count': 22, 'avg_salary': 55000, 'min': 42000, 'max': 75000},
            'HR': {'count': 12, 'avg_salary': 58000, 'min': 45000, 'max': 80000},
            'Finance': {'count': 15, 'avg_salary': 72000, 'min': 55000, 'max': 95000},
            'Customer Support': {'count': 16, 'avg_salary': 48000, 'min': 38000, 'max': 65000}
        }
        
        # Pay distribution
        distribution = [
            {'range': '$40-60k', 'count': 45, 'percentage': 28.8, 'avg_salary': 52000},
            {'range': '$60-80k', 'count': 67, 'percentage': 42.9, 'avg_salary': 71500},
            {'range': '$80-120k', 'count': 32, 'percentage': 20.5, 'avg_salary': 95800},
            {'range': '$120k+', 'count': 12, 'percentage': 7.7, 'avg_salary': 145000}
        ]
        
        return jsonify({
            'summary': {
                'total_employees': total_employees,
                'avg_salary': avg_salary,
                'total_compensation': total_compensation,
                'pay_equity_score': 94,
                'market_reviews_due': 8
            },
            'departments': departments,
            'distribution': distribution,
            'alerts': [
                {
                    'type': 'warning',
                    'message': '3 positions show potential pay gaps requiring review',
                    'priority': 'high'
                },
                {
                    'type': 'info',
                    'message': 'Annual market rate refresh due in 30 days',
                    'priority': 'medium'
                }
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/salary-bands', methods=['GET'])
@jwt_required()
def get_salary_bands():
    """Get salary bands and pay grades"""
    try:
        bands_data = []
        for band in mock_salary_bands:
            bands_data.append({
                'id': band.id,
                'grade': band.grade,
                'title': band.title,
                'min_salary': band.min_salary,
                'max_salary': band.max_salary,
                'midpoint': band.midpoint,
                'department': band.department,
                'employee_count': band.employee_count,
                'spread': round(((band.max_salary - band.min_salary) / band.midpoint) * 100, 1)
            })
        
        return jsonify({
            'salary_bands': bands_data,
            'total_bands': len(bands_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/salary-bands', methods=['POST'])
@jwt_required()
def create_salary_band():
    """Create a new salary band"""
    try:
        data = request.json
        
        required_fields = ['grade', 'title', 'min_salary', 'max_salary']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Calculate midpoint
        midpoint = (data['min_salary'] + data['max_salary']) / 2
        
        new_id = max([band.id for band in mock_salary_bands]) + 1
        new_band = SalaryBand(
            id=new_id,
            grade=data['grade'],
            title=data['title'],
            min_salary=data['min_salary'],
            max_salary=data['max_salary'],
            midpoint=midpoint,
            department=data.get('department', 'All')
        )
        
        mock_salary_bands.append(new_band)
        
        return jsonify({
            'message': 'Salary band created successfully',
            'band': {
                'id': new_band.id,
                'grade': new_band.grade,
                'title': new_band.title,
                'midpoint': new_band.midpoint
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/pay-equity', methods=['GET'])
@jwt_required()
def get_pay_equity_analysis():
    """Get pay equity analysis"""
    try:
        # Mock pay equity data
        gender_analysis = {
            'overall_ratio': 0.96,
            'status': 'within_range',
            'departments': [
                {'name': 'Engineering', 'male_avg': 86500, 'female_avg': 83200, 'ratio': 0.96, 'status': 'good'},
                {'name': 'Sales', 'male_avg': 67800, 'female_avg': 66100, 'ratio': 0.97, 'status': 'good'},
                {'name': 'Marketing', 'male_avg': 64200, 'female_avg': 59800, 'ratio': 0.93, 'status': 'review'},
                {'name': 'Operations', 'male_avg': 56200, 'female_avg': 53800, 'ratio': 0.96, 'status': 'good'}
            ]
        }
        
        position_analysis = [
            {'position': 'Software Engineer', 'ratio': 0.98, 'male_count': 15, 'female_count': 8, 'status': 'good'},
            {'position': 'Sales Representative', 'ratio': 0.92, 'male_count': 12, 'female_count': 9, 'status': 'review'},
            {'position': 'Marketing Specialist', 'ratio': 0.89, 'male_count': 6, 'female_count': 12, 'status': 'action_needed'},
            {'position': 'Project Manager', 'ratio': 1.02, 'male_count': 8, 'female_count': 7, 'status': 'good'}
        ]
        
        return jsonify({
            'gender_analysis': gender_analysis,
            'position_analysis': position_analysis,
            'recommendations': [
                'Review Marketing Specialist compensation structure',
                'Analyze Sales Representative pay disparities',
                'Implement regular pay equity audits',
                'Update compensation guidelines'
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/market-data', methods=['GET'])
@jwt_required()
def get_market_data():
    """Get market benchmark data"""
    try:
        benchmarks_data = []
        for benchmark in mock_benchmarks:
            # Calculate market position
            if benchmark.our_avg < benchmark.market_25th:
                position = 'below_market'
                action = 'Review & Adjust'
            elif benchmark.our_avg > benchmark.market_75th:
                position = 'above_market'
                action = 'Monitor'
            else:
                position = 'at_market'
                action = 'None'
            
            benchmarks_data.append({
                'position': benchmark.position,
                'our_avg': benchmark.our_avg,
                'market_25th': benchmark.market_25th,
                'market_50th': benchmark.market_50th,
                'market_75th': benchmark.market_75th,
                'market_position': position,
                'action_needed': action,
                'source': benchmark.source,
                'last_updated': benchmark.last_updated.strftime('%b %Y'),
                'percentile': round((benchmark.our_avg - benchmark.market_25th) / 
                                 (benchmark.market_75th - benchmark.market_25th) * 100, 1)
            })
        
        return jsonify({
            'benchmarks': benchmarks_data,
            'sources': [
                {'name': 'PayScale', 'last_updated': 'Sep 2024'},
                {'name': 'Glassdoor', 'last_updated': 'Aug 2024'},
                {'name': 'Salary.com', 'last_updated': 'Sep 2024'},
                {'name': 'Industry Survey', 'last_updated': 'Jun 2024'}
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/budget', methods=['GET'])
@jwt_required()
def get_budget_analysis():
    """Get compensation budget analysis"""
    try:
        # Mock budget data
        budget_2024 = {
            'Engineering': {'budget': 3800000, 'actual': 3825000, 'variance': 25000},
            'Sales': {'budget': 1820000, 'actual': 1785000, 'variance': -35000},
            'Marketing': {'budget': 1116000, 'actual': 1098000, 'variance': -18000},
            'Operations': {'budget': 1210000, 'actual': 1232000, 'variance': 22000},
            'HR': {'budget': 696000, 'actual': 684000, 'variance': -12000},
            'Finance': {'budget': 1080000, 'actual': 1095000, 'variance': 15000}
        }
        
        # Calculate totals
        total_budget = sum(dept['budget'] for dept in budget_2024.values())
        total_actual = sum(dept['actual'] for dept in budget_2024.values())
        total_variance = total_actual - total_budget
        variance_percent = (total_variance / total_budget) * 100
        
        return jsonify({
            'budget_2024': {
                'departments': budget_2024,
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_variance': total_variance,
                'variance_percent': round(variance_percent, 2)
            },
            'budget_categories': {
                'base_salary': {'budget': 8500000, 'actual': 8515000},
                'bonuses': {'budget': 850000, 'actual': 890000},
                'benefits': {'budget': 1275000, 'actual': 1284000},
                'payroll_taxes': {'budget': 765000, 'actual': 778000}
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/budget/calculate', methods=['POST'])
@jwt_required()
def calculate_budget():
    """Calculate future budget projections"""
    try:
        data = request.json
        
        # Budget parameters
        merit_increase = data.get('merit_increase', 3.5)
        promotion_budget = data.get('promotion_budget', 1.5)
        market_adjustment = data.get('market_adjustment', 1.0)
        new_hire_budget = data.get('new_hire_budget', 500000)
        
        # Current budget
        current_total = 9600000
        
        # Calculate increases
        merit_cost = current_total * (merit_increase / 100)
        promotion_cost = current_total * (promotion_budget / 100)
        market_cost = current_total * (market_adjustment / 100)
        
        # Calculate new budget
        projected_budget = current_total + merit_cost + promotion_cost + market_cost + new_hire_budget
        total_increase_percent = ((projected_budget - current_total) / current_total) * 100
        
        avg_per_employee = projected_budget / 156  # Current employee count
        
        return jsonify({
            'projections': {
                'current_budget': current_total,
                'merit_cost': merit_cost,
                'promotion_cost': promotion_cost,
                'market_adjustment_cost': market_cost,
                'new_hire_budget': new_hire_budget,
                'projected_budget': projected_budget,
                'total_increase': projected_budget - current_total,
                'increase_percent': round(total_increase_percent, 2),
                'avg_per_employee': round(avg_per_employee, 0)
            },
            'breakdown': {
                'merit_increases': f'{merit_increase}%',
                'promotions': f'{promotion_budget}%',
                'market_adjustments': f'{market_adjustment}%',
                'new_hires': f'${new_hire_budget:,.0f}'
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/employees/<int:employee_id>/analysis', methods=['GET'])
@jwt_required()
def get_employee_compensation_analysis(employee_id):
    """Get individual employee compensation analysis"""
    try:
        # Mock employee compensation data
        analysis = {
            'employee_id': employee_id,
            'current_salary': 75000,
            'salary_band': {
                'grade': 'Grade 3',
                'min': 65000,
                'max': 85000,
                'midpoint': 75000
            },
            'compa_ratio': 1.0,
            'market_position': {
                'percentile': 50,
                'market_median': 75000,
                'variance_from_market': 0
            },
            'pay_equity': {
                'peer_avg': 74800,
                'variance': 200,
                'status': 'equitable'
            },
            'recommendations': [
                'Salary is appropriately positioned within band',
                'Consider for merit increase based on performance',
                'Market competitive'
            ]
        }
        
        return jsonify({
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compensation.route('/api/compensation/reports/export', methods=['POST'])
@jwt_required()
def export_compensation_report():
    """Export compensation reports"""
    try:
        data = request.json
        report_type = data.get('type', 'overview')
        format_type = data.get('format', 'excel')
        
        # Mock export
        export_id = f'comp_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        return jsonify({
            'message': f'Compensation {report_type} report export initiated',
            'export_id': export_id,
            'format': format_type,
            'estimated_completion': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'download_url': f'/downloads/{export_id}.{format_type}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500