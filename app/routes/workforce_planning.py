from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
import calendar

workforce_planning_bp = Blueprint('workforce_planning', __name__)

@workforce_planning_bp.route('/workforce-planning')
def workforce_planning():
    """Strategic Workforce Planning dashboard"""
    return render_template('workforce_planning.html')

@workforce_planning_bp.route('/api/workforce-planning/dashboard', methods=['GET'])
def get_workforce_planning_dashboard():
    """Get Workforce Planning dashboard statistics"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'current_headcount': 450,
                'projected_growth_6m': 75,
                'open_positions': 23,
                'critical_skill_gaps': 8,
                'succession_ready_candidates': 34,
                'avg_time_to_fill': 35,
                'retention_risk_employees': 12,
                'workforce_optimization_score': 87.5
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/demand-forecast', methods=['GET'])
def get_demand_forecast():
    """Get workforce demand forecasting data"""
    try:
        period = request.args.get('period', '12')  # months
        department = request.args.get('department', 'all')
        
        # Mock demand forecasting data
        forecast_data = {
            'summary': {
                'current_headcount': 450,
                'projected_headcount_q1': 475,
                'projected_headcount_q2': 495,
                'projected_headcount_q3': 510,
                'projected_headcount_q4': 525,
                'growth_rate': 16.7,
                'confidence_level': 94.2,
                'last_updated': datetime.now().isoformat()
            },
            'departments': [
                {
                    'id': 1,
                    'name': 'Information Technology',
                    'current_count': 85,
                    'projections': {
                        'q1_2026': 95,
                        'q2_2026': 102,
                        'q3_2026': 110,
                        'q4_2026': 118
                    },
                    'growth_rate': 38.8,
                    'priority': 'critical',
                    'drivers': [
                        'AI/ML product development',
                        'Digital transformation',
                        'Cloud migration projects'
                    ],
                    'risks': [
                        'Skills shortage in AI/ML',
                        'Competition for talent',
                        'Remote work preferences'
                    ]
                },
                {
                    'id': 2,
                    'name': 'Marketing',
                    'current_count': 32,
                    'projections': {
                        'q1_2026': 36,
                        'q2_2026': 40,
                        'q3_2026': 42,
                        'q4_2026': 45
                    },
                    'growth_rate': 40.6,
                    'priority': 'high',
                    'drivers': [
                        'Market expansion',
                        'Digital marketing growth',
                        'Brand development'
                    ],
                    'risks': [
                        'Budget constraints',
                        'Performance marketing skills gap',
                        'Changing customer preferences'
                    ]
                },
                {
                    'id': 3,
                    'name': 'Finance',
                    'current_count': 28,
                    'projections': {
                        'q1_2026': 30,
                        'q2_2026': 31,
                        'q3_2026': 32,
                        'q4_2026': 33
                    },
                    'growth_rate': 17.9,
                    'priority': 'medium',
                    'drivers': [
                        'Regulatory compliance',
                        'Financial planning expansion',
                        'Risk management'
                    ],
                    'risks': [
                        'Retirement wave expected',
                        'Specialized skills required',
                        'Regulatory changes'
                    ]
                },
                {
                    'id': 4,
                    'name': 'Operations',
                    'current_count': 65,
                    'projections': {
                        'q1_2026': 70,
                        'q2_2026': 75,
                        'q3_2026': 78,
                        'q4_2026': 82
                    },
                    'growth_rate': 26.2,
                    'priority': 'high',
                    'drivers': [
                        'Process optimization',
                        'Quality assurance',
                        'Customer service expansion'
                    ],
                    'risks': [
                        'Automation impact',
                        'Process standardization',
                        'Training requirements'
                    ]
                }
            ],
            'external_factors': {
                'market_conditions': 'Growing',
                'competition_level': 'High',
                'talent_availability': 'Limited',
                'economic_outlook': 'Positive',
                'technology_trends': ['AI/ML', 'Cloud Computing', 'Automation']
            }
        }
        
        # Apply department filter
        if department != 'all':
            forecast_data['departments'] = [
                dept for dept in forecast_data['departments'] 
                if dept['name'].lower() == department.lower()
            ]
        
        return jsonify({
            'success': True,
            'data': forecast_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/capacity-analysis', methods=['GET'])
def get_capacity_analysis():
    """Get workforce capacity analysis"""
    try:
        department = request.args.get('department', 'all')
        
        # Mock capacity analysis data
        capacity_data = {
            'summary': {
                'total_capacity': 450,
                'current_utilization': 87.5,
                'optimal_utilization': 85.0,
                'capacity_gaps': 23,
                'over_utilized_departments': 2,
                'under_utilized_departments': 1
            },
            'departments': [
                {
                    'id': 1,
                    'name': 'Information Technology',
                    'current_staff': 85,
                    'optimal_capacity': 95,
                    'utilization_rate': 89.5,
                    'workload_trend': 'increasing',
                    'recommended_action': 'Hire 10 engineers',
                    'timeline': 'Q1 2026',
                    'cost_impact': 850000,
                    'skills_needed': ['Python', 'AI/ML', 'Cloud Architecture'],
                    'capacity_breakdown': {
                        'senior': {'current': 25, 'optimal': 30, 'gap': 5},
                        'mid': {'current': 35, 'optimal': 40, 'gap': 5},
                        'junior': {'current': 25, 'optimal': 25, 'gap': 0}
                    }
                },
                {
                    'id': 2,
                    'name': 'Marketing',
                    'current_staff': 32,
                    'optimal_capacity': 35,
                    'utilization_rate': 91.4,
                    'workload_trend': 'stable',
                    'recommended_action': 'Add 3 specialists',
                    'timeline': 'Q2 2026',
                    'cost_impact': 240000,
                    'skills_needed': ['Digital Marketing', 'Analytics', 'Content Strategy'],
                    'capacity_breakdown': {
                        'senior': {'current': 8, 'optimal': 10, 'gap': 2},
                        'mid': {'current': 15, 'optimal': 15, 'gap': 0},
                        'junior': {'current': 9, 'optimal': 10, 'gap': 1}
                    }
                },
                {
                    'id': 3,
                    'name': 'Finance',
                    'current_staff': 28,
                    'optimal_capacity': 30,
                    'utilization_rate': 93.3,
                    'workload_trend': 'stable',
                    'recommended_action': 'Succession planning',
                    'timeline': 'Q3 2026',
                    'cost_impact': 180000,
                    'skills_needed': ['Financial Analysis', 'Risk Management', 'Compliance'],
                    'capacity_breakdown': {
                        'senior': {'current': 8, 'optimal': 8, 'gap': 0},
                        'mid': {'current': 12, 'optimal': 14, 'gap': 2},
                        'junior': {'current': 8, 'optimal': 8, 'gap': 0}
                    }
                },
                {
                    'id': 4,
                    'name': 'Operations',
                    'current_staff': 65,
                    'optimal_capacity': 70,
                    'utilization_rate': 92.9,
                    'workload_trend': 'increasing',
                    'recommended_action': 'Process optimization',
                    'timeline': 'Q1 2026',
                    'cost_impact': 350000,
                    'skills_needed': ['Process Management', 'Quality Control', 'Customer Service'],
                    'capacity_breakdown': {
                        'senior': {'current': 15, 'optimal': 18, 'gap': 3},
                        'mid': {'current': 30, 'optimal': 32, 'gap': 2},
                        'junior': {'current': 20, 'optimal': 20, 'gap': 0}
                    }
                }
            ],
            'resource_allocation': {
                'by_quarter': [
                    {'quarter': 'Q1 2026', 'planned_hires': 15, 'budget': 1200000},
                    {'quarter': 'Q2 2026', 'planned_hires': 12, 'budget': 960000},
                    {'quarter': 'Q3 2026', 'planned_hires': 8, 'budget': 640000},
                    {'quarter': 'Q4 2026', 'planned_hires': 10, 'budget': 800000}
                ],
                'total_investment': 3600000
            }
        }
        
        # Apply department filter
        if department != 'all':
            capacity_data['departments'] = [
                dept for dept in capacity_data['departments'] 
                if dept['name'].lower() == department.lower()
            ]
        
        return jsonify({
            'success': True,
            'data': capacity_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/skills-analysis', methods=['GET'])
def get_skills_analysis():
    """Get comprehensive skills gap analysis"""
    try:
        department = request.args.get('department', 'all')
        skill_category = request.args.get('category', 'all')
        
        # Mock skills analysis data
        skills_data = {
            'summary': {
                'total_skill_gaps': 43,
                'critical_gaps': 23,
                'high_priority_gaps': 12,
                'medium_priority_gaps': 8,
                'training_programs_active': 15,
                'estimated_training_cost': 450000,
                'time_to_close_gaps': 8  # months
            },
            'skill_categories': [
                {
                    'id': 1,
                    'name': 'Technical Skills',
                    'subcategories': [
                        {
                            'name': 'Artificial Intelligence/Machine Learning',
                            'required_level': 'Advanced',
                            'current_level': 'Intermediate',
                            'gap_severity': 'critical',
                            'affected_roles': 15,
                            'departments': ['IT', 'Operations'],
                            'training_plan': 'External hiring + certification program',
                            'timeline': '6 months',
                            'budget': 180000,
                            'roi_projection': 3.2
                        },
                        {
                            'name': 'Cloud Architecture',
                            'required_level': 'Expert',
                            'current_level': 'Advanced',
                            'gap_severity': 'high',
                            'affected_roles': 8,
                            'departments': ['IT'],
                            'training_plan': 'AWS/Azure certification',
                            'timeline': '4 months',
                            'budget': 80000,
                            'roi_projection': 2.8
                        },
                        {
                            'name': 'Data Analytics',
                            'required_level': 'Advanced',
                            'current_level': 'Intermediate',
                            'gap_severity': 'high',
                            'affected_roles': 12,
                            'departments': ['Marketing', 'Finance'],
                            'training_plan': 'Data science bootcamp',
                            'timeline': '5 months',
                            'budget': 120000,
                            'roi_projection': 2.5
                        }
                    ]
                },
                {
                    'id': 2,
                    'name': 'Leadership & Management',
                    'subcategories': [
                        {
                            'name': 'Strategic Leadership',
                            'required_level': 'Advanced',
                            'current_level': 'Intermediate',
                            'gap_severity': 'high',
                            'affected_roles': 8,
                            'departments': ['All'],
                            'training_plan': 'Leadership development program',
                            'timeline': '8 months',
                            'budget': 160000,
                            'roi_projection': 4.1
                        },
                        {
                            'name': 'Change Management',
                            'required_level': 'Advanced',
                            'current_level': 'Basic',
                            'gap_severity': 'medium',
                            'affected_roles': 6,
                            'departments': ['Operations', 'HR'],
                            'training_plan': 'Change management certification',
                            'timeline': '3 months',
                            'budget': 60000,
                            'roi_projection': 2.2
                        }
                    ]
                },
                {
                    'id': 3,
                    'name': 'Digital & Communication',
                    'subcategories': [
                        {
                            'name': 'Digital Marketing',
                            'required_level': 'Advanced',
                            'current_level': 'Intermediate',
                            'gap_severity': 'medium',
                            'affected_roles': 12,
                            'departments': ['Marketing'],
                            'training_plan': 'Digital marketing workshops',
                            'timeline': '3 months',
                            'budget': 90000,
                            'roi_projection': 2.8
                        }
                    ]
                }
            ],
            'department_skill_matrix': {
                'Information Technology': {
                    'current_score': 7.2,
                    'target_score': 8.5,
                    'gap': 1.3,
                    'priority_skills': ['AI/ML', 'Cloud Architecture', 'DevOps']
                },
                'Marketing': {
                    'current_score': 6.8,
                    'target_score': 8.0,
                    'gap': 1.2,
                    'priority_skills': ['Digital Marketing', 'Analytics', 'Marketing Automation']
                },
                'Finance': {
                    'current_score': 7.5,
                    'target_score': 8.2,
                    'gap': 0.7,
                    'priority_skills': ['Financial Modeling', 'Risk Analytics', 'Compliance']
                },
                'Operations': {
                    'current_score': 6.9,
                    'target_score': 7.8,
                    'gap': 0.9,
                    'priority_skills': ['Process Optimization', 'Quality Management', 'Automation']
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': skills_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/scenarios', methods=['GET'])
def get_scenarios():
    """Get workforce planning scenarios"""
    try:
        # Mock scenario planning data
        scenarios_data = {
            'scenarios': [
                {
                    'id': 1,
                    'name': 'Conservative Growth',
                    'description': '5% annual growth, focus on efficiency and optimization',
                    'assumptions': {
                        'growth_rate': 5,
                        'market_conditions': 'stable',
                        'budget_increase': 3,
                        'attrition_rate': 8
                    },
                    'projections': {
                        'new_hires': 23,
                        'total_headcount': 473,
                        'budget_required': 1200000,
                        'time_to_capacity': 9
                    },
                    'risks': ['Limited growth potential', 'Talent retention challenges'],
                    'benefits': ['Lower financial risk', 'Sustainable growth', 'Higher profit margins']
                },
                {
                    'id': 2,
                    'name': 'Moderate Expansion',
                    'description': '12% annual growth, balanced approach to scaling',
                    'assumptions': {
                        'growth_rate': 12,
                        'market_conditions': 'growing',
                        'budget_increase': 8,
                        'attrition_rate': 10
                    },
                    'projections': {
                        'new_hires': 54,
                        'total_headcount': 504,
                        'budget_required': 2800000,
                        'time_to_capacity': 12
                    },
                    'risks': ['Moderate hiring challenges', 'Training capacity'],
                    'benefits': ['Balanced growth', 'Market competitiveness', 'Skill development'],
                    'recommended': True
                },
                {
                    'id': 3,
                    'name': 'Aggressive Growth',
                    'description': '25% annual growth, rapid scaling and market capture',
                    'assumptions': {
                        'growth_rate': 25,
                        'market_conditions': 'booming',
                        'budget_increase': 18,
                        'attrition_rate': 15
                    },
                    'projections': {
                        'new_hires': 113,
                        'total_headcount': 563,
                        'budget_required': 5800000,
                        'time_to_capacity': 18
                    },
                    'risks': ['High hiring risk', 'Cultural challenges', 'Quality concerns'],
                    'benefits': ['Market leadership', 'Revenue acceleration', 'Innovation capacity']
                }
            ],
            'scenario_comparison': {
                'metrics': ['ROI', 'Risk Level', 'Time to Market', 'Resource Requirements'],
                'conservative': [85, 25, 95, 40],
                'moderate': [92, 45, 80, 65],
                'aggressive': [78, 85, 60, 95]
            },
            'recommended_scenario': 2,
            'recommendation_rationale': 'Moderate expansion provides the best balance of growth potential and manageable risk while maintaining quality standards.'
        }
        
        return jsonify({
            'success': True,
            'data': scenarios_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/strategic-insights', methods=['GET'])
def get_strategic_insights():
    """Get strategic workforce insights and recommendations"""
    try:
        # Mock strategic insights data
        insights_data = {
            'key_insights': [
                {
                    'id': 1,
                    'title': 'Critical AI/ML Skills Gap',
                    'severity': 'critical',
                    'description': 'Immediate hiring required for Q1 product launch success',
                    'impact': 'High revenue risk if not addressed',
                    'recommendation': 'Hire 10 AI/ML engineers by Q1 2026',
                    'timeline': '3 months',
                    'cost': 850000,
                    'roi': 3.2
                },
                {
                    'id': 2,
                    'title': 'Leadership Pipeline Gap',
                    'severity': 'high',
                    'description': 'Upcoming retirements in Finance will create leadership vacuum',
                    'impact': 'Succession planning required to maintain continuity',
                    'recommendation': 'Implement leadership development program',
                    'timeline': '6 months',
                    'cost': 160000,
                    'roi': 4.1
                },
                {
                    'id': 3,
                    'title': 'Operations Capacity Optimization',
                    'severity': 'medium',
                    'description': 'Workload redistribution can improve efficiency',
                    'impact': 'Cost savings and improved employee satisfaction',
                    'recommendation': 'Process optimization and workload rebalancing',
                    'timeline': '4 months',
                    'cost': 120000,
                    'roi': 2.8
                }
            ],
            'performance_metrics': {
                'forecast_accuracy': {
                    'current': 94.2,
                    'target': 96.0,
                    'trend': 'improving',
                    'factors': ['Better data quality', 'Improved algorithms', 'Regular updates']
                },
                'cost_efficiency': {
                    'cost_per_hire': 15000,
                    'time_to_fill': 45,
                    'retention_rate': 92.5,
                    'training_roi': 3.2
                },
                'strategic_alignment': {
                    'skills_alignment': 87,
                    'capacity_match': 89,
                    'succession_readiness': 78
                }
            },
            'investment_analysis': {
                'total_investment_required': 3600000,
                'projected_savings': 2800000,
                'net_roi': 320,
                'payback_period': 18,
                'risk_adjusted_roi': 285
            },
            'market_intelligence': {
                'talent_market_conditions': 'Competitive',
                'salary_trends': '+8% annually',
                'skill_demand_trends': ['AI/ML', 'Cloud', 'Cybersecurity', 'Data Analytics'],
                'competitive_landscape': 'High competition for technical talent',
                'remote_work_impact': 'Expanded talent pool, increased retention challenges'
            },
            'recommendations': {
                'immediate_actions': [
                    'Launch AI/ML recruitment campaign',
                    'Initiate leadership development program',
                    'Implement skills assessment across all departments'
                ],
                'short_term_goals': [
                    'Close critical skill gaps within 6 months',
                    'Establish succession plans for key roles',
                    'Optimize capacity utilization'
                ],
                'long_term_strategy': [
                    'Build internal AI/ML capability',
                    'Create comprehensive leadership pipeline',
                    'Develop adaptive workforce planning model'
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'data': insights_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/create-plan', methods=['POST'])
def create_workforce_plan():
    """Create a new workforce plan"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'scenario_id', 'departments', 'timeline']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock plan creation
        plan = {
            'id': f"WFP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': data['name'],
            'scenario_id': data['scenario_id'],
            'departments': data['departments'],
            'timeline': data['timeline'],
            'objectives': data.get('objectives', []),
            'budget': data.get('budget', 0),
            'created_by': data.get('created_by', 'System'),
            'created_at': datetime.now().isoformat(),
            'status': 'draft',
            'approval_status': 'pending',
            'milestones': data.get('milestones', []),
            'success_metrics': data.get('success_metrics', [])
        }
        
        return jsonify({
            'success': True,
            'message': 'Workforce plan created successfully',
            'data': plan
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/plans', methods=['GET'])
def get_workforce_plans():
    """Get all workforce plans"""
    try:
        status = request.args.get('status', 'all')
        
        # Mock workforce plans data
        plans = [
            {
                'id': 'WFP20251001123000',
                'name': 'Q1 2026 Expansion Plan',
                'scenario': 'Moderate Expansion',
                'status': 'active',
                'approval_status': 'approved',
                'created_date': '2025-10-01',
                'target_headcount': 504,
                'budget': 2800000,
                'progress': 65,
                'departments': ['IT', 'Marketing', 'Operations']
            },
            {
                'id': 'WFP20250915094500',
                'name': 'AI Skills Development Initiative',
                'scenario': 'Conservative Growth',
                'status': 'in_progress',
                'approval_status': 'approved',
                'created_date': '2025-09-15',
                'target_headcount': 473,
                'budget': 1200000,
                'progress': 80,
                'departments': ['IT']
            }
        ]
        
        # Apply status filter
        if status != 'all':
            plans = [plan for plan in plans if plan['status'] == status]
        
        return jsonify({
            'success': True,
            'data': plans
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@workforce_planning_bp.route('/api/workforce/reports/generate', methods=['POST'])
def generate_workforce_report():
    """Generate workforce planning reports"""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'demand_forecast')
        date_range = data.get('date_range', '12_months')
        departments = data.get('departments', [])
        
        # Mock report generation
        report = {
            'id': f"WFR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': report_type,
            'title': f"Workforce {report_type.replace('_', ' ').title()} Report",
            'date_range': date_range,
            'departments': departments,
            'generated_by': 'System',
            'generated_at': datetime.now().isoformat(),
            'status': 'ready',
            'file_url': f"/reports/workforce/{report_type}-{datetime.now().strftime('%Y%m%d')}.pdf",
            'summary': {
                'total_insights': 15,
                'critical_findings': 3,
                'recommendations': 8,
                'projected_savings': 2800000
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'data': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500