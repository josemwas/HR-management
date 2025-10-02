from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta

succession_planning_bp = Blueprint('succession_planning', __name__)

@succession_planning_bp.route('/succession-planning')
def succession_planning():
    """Succession Planning & Leadership Development dashboard"""
    return render_template('succession_planning.html')

@succession_planning_bp.route('/api/succession-planning/dashboard', methods=['GET'])
def get_succession_planning_dashboard():
    """Get Succession Planning dashboard statistics"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'key_positions_total': 45,
                'positions_with_successors': 32,
                'succession_coverage_rate': 71.1,
                'high_risk_positions': 8,
                'ready_now_candidates': 15,
                'development_programs_active': 12,
                'avg_successor_readiness': 78.5,
                'leadership_pipeline_strength': 82.3
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@succession_planning_bp.route('/api/succession/key-positions', methods=['GET'])
def get_key_positions():
    """Get key positions and succession plans"""
    try:
        department = request.args.get('department', 'all')
        risk_level = request.args.get('risk_level', 'all')
        
        # Mock key positions data
        key_positions = [
            {
                'id': 1,
                'position_title': 'Chief Executive Officer',
                'incumbent': {
                    'name': 'Robert Martinez',
                    'employee_id': 'CEO001',
                    'tenure': '8 years',
                    'retirement_date': '2026-06-30',
                    'performance_rating': 'Excellent'
                },
                'department': 'Executive',
                'level': 'C-Level',
                'risk_level': 'high',
                'business_impact': 'critical',
                'successors': [
                    {
                        'name': 'Sarah Chen',
                        'current_role': 'VP Technology',
                        'readiness_level': 'ready',
                        'development_time': '0 months',
                        'readiness_score': 95
                    },
                    {
                        'name': 'Michael Davis',
                        'current_role': 'VP Operations',
                        'readiness_level': 'developing',
                        'development_time': '18 months',
                        'readiness_score': 75
                    }
                ],
                'development_programs': ['Executive Leadership Program', 'Strategic Planning Workshop'],
                'succession_timeline': '6 months',
                'last_review': '2025-09-15',
                'next_review': '2025-12-15'
            },
            {
                'id': 2,
                'position_title': 'VP Technology',
                'incumbent': {
                    'name': 'Sarah Chen',
                    'employee_id': 'VP001',
                    'tenure': '5 years',
                    'retirement_date': None,
                    'performance_rating': 'Outstanding'
                },
                'department': 'Technology',
                'level': 'VP',
                'risk_level': 'low',
                'business_impact': 'high',
                'successors': [
                    {
                        'name': 'Alex Kumar',
                        'current_role': 'Engineering Director',
                        'readiness_level': 'ready',
                        'development_time': '0 months',
                        'readiness_score': 88
                    },
                    {
                        'name': 'Lisa Wong',
                        'current_role': 'Principal Architect',
                        'readiness_level': 'ready',
                        'development_time': '3 months',
                        'readiness_score': 85
                    }
                ],
                'development_programs': ['Technical Leadership Track', 'Mentorship Program'],
                'succession_timeline': '3 months',
                'last_review': '2025-08-20',
                'next_review': '2025-11-20'
            },
            {
                'id': 3,
                'position_title': 'Marketing Director',
                'incumbent': {
                    'name': 'Jessica Adams',
                    'employee_id': 'MKT001',
                    'tenure': '3 years',
                    'retirement_date': None,
                    'performance_rating': 'Excellent'
                },
                'department': 'Marketing',
                'level': 'Director',
                'risk_level': 'high',
                'business_impact': 'medium',
                'successors': [],
                'development_programs': [],
                'succession_timeline': 'No plan',
                'last_review': '2025-07-10',
                'next_review': '2025-10-10'
            },
            {
                'id': 4,
                'position_title': 'VP Finance',
                'incumbent': {
                    'name': 'Emily Brown',
                    'employee_id': 'FIN001',
                    'tenure': '6 years',
                    'retirement_date': '2028-12-31',
                    'performance_rating': 'Excellent'
                },
                'department': 'Finance',
                'level': 'VP',
                'risk_level': 'medium',
                'business_impact': 'high',
                'successors': [
                    {
                        'name': 'David Kim',
                        'current_role': 'Finance Director',
                        'readiness_level': 'developing',
                        'development_time': '12 months',
                        'readiness_score': 78
                    }
                ],
                'development_programs': ['Financial Leadership Program', 'Strategic Finance Course'],
                'succession_timeline': '12 months',
                'last_review': '2025-09-01',
                'next_review': '2025-12-01'
            }
        ]
        
        # Apply filters
        if department != 'all':
            key_positions = [pos for pos in key_positions if pos['department'].lower() == department.lower()]
        
        if risk_level != 'all':
            key_positions = [pos for pos in key_positions if pos['risk_level'] == risk_level]
        
        return jsonify({
            'success': True,
            'data': key_positions,
            'summary': {
                'total_positions': len(key_positions),
                'high_risk': len([pos for pos in key_positions if pos['risk_level'] == 'high']),
                'medium_risk': len([pos for pos in key_positions if pos['risk_level'] == 'medium']),
                'low_risk': len([pos for pos in key_positions if pos['risk_level'] == 'low']),
                'positions_with_successors': len([pos for pos in key_positions if pos['successors']]),
                'positions_without_successors': len([pos for pos in key_positions if not pos['successors']])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/talent-pipeline', methods=['GET'])
def get_talent_pipeline():
    """Get talent pipeline and succession candidates"""
    try:
        readiness_level = request.args.get('readiness_level', 'all')
        department = request.args.get('department', 'all')
        
        # Mock talent pipeline data
        pipeline_candidates = [
            {
                'id': 1,
                'candidate': {
                    'name': 'Sarah Chen',
                    'employee_id': 'VP001',
                    'current_role': 'VP Technology',
                    'department': 'Technology',
                    'hire_date': '2020-03-15',
                    'performance_rating': 'Outstanding'
                },
                'target_positions': ['Chief Executive Officer'],
                'readiness_level': 'ready',
                'readiness_score': 95,
                'development_stage': 'Advanced Leadership',
                'development_programs': [
                    {
                        'name': 'Executive Leadership Program',
                        'status': 'completed',
                        'completion_date': '2025-08-15'
                    },
                    {
                        'name': 'Strategic Planning Workshop',
                        'status': 'in_progress',
                        'expected_completion': '2025-11-30'
                    }
                ],
                'skills_assessment': {
                    'leadership': 92,
                    'strategic_thinking': 88,
                    'communication': 95,
                    'technical_expertise': 90,
                    'decision_making': 87
                },
                'development_goals': [
                    'Complete strategic planning certification',
                    'Lead cross-functional initiative',
                    'Board presentation experience'
                ],
                'mentor': 'Robert Martinez',
                'estimated_promotion_date': '2026-01-01'
            },
            {
                'id': 2,
                'candidate': {
                    'name': 'Alex Kumar',
                    'employee_id': 'ENG001',
                    'current_role': 'Engineering Director',
                    'department': 'Technology',
                    'hire_date': '2019-07-20',
                    'performance_rating': 'Excellent'
                },
                'target_positions': ['VP Technology'],
                'readiness_level': 'ready',
                'readiness_score': 88,
                'development_stage': 'Technical Leadership',
                'development_programs': [
                    {
                        'name': 'Technical Leadership Track',
                        'status': 'completed',
                        'completion_date': '2025-06-30'
                    },
                    {
                        'name': 'Management Excellence Program',
                        'status': 'in_progress',
                        'expected_completion': '2025-12-15'
                    }
                ],
                'skills_assessment': {
                    'leadership': 85,
                    'strategic_thinking': 82,
                    'communication': 88,
                    'technical_expertise': 95,
                    'decision_making': 83
                },
                'development_goals': [
                    'Enhance business acumen',
                    'Develop stakeholder management skills',
                    'Complete P&L responsibility training'
                ],
                'mentor': 'Sarah Chen',
                'estimated_promotion_date': '2026-04-01'
            },
            {
                'id': 3,
                'candidate': {
                    'name': 'Tom Wilson',
                    'employee_id': 'OPS001',
                    'current_role': 'Operations Manager',
                    'department': 'Operations',
                    'hire_date': '2021-01-10',
                    'performance_rating': 'Excellent'
                },
                'target_positions': ['VP Operations'],
                'readiness_level': 'developing',
                'readiness_score': 72,
                'development_stage': 'Management Excellence',
                'development_programs': [
                    {
                        'name': 'Management Excellence Program',
                        'status': 'in_progress',
                        'expected_completion': '2026-03-30'
                    },
                    {
                        'name': 'Operations Leadership Course',
                        'status': 'planned',
                        'expected_start': '2026-01-15'
                    }
                ],
                'skills_assessment': {
                    'leadership': 75,
                    'strategic_thinking': 68,
                    'communication': 80,
                    'technical_expertise': 85,
                    'decision_making': 72
                },
                'development_goals': [
                    'Develop strategic planning skills',
                    'Improve cross-functional collaboration',
                    'Complete finance for non-finance managers'
                ],
                'mentor': 'Michael Davis',
                'estimated_promotion_date': '2026-10-01'
            }
        ]
        
        # Apply filters
        if readiness_level != 'all':
            pipeline_candidates = [cand for cand in pipeline_candidates if cand['readiness_level'] == readiness_level]
        
        if department != 'all':
            pipeline_candidates = [cand for cand in pipeline_candidates if cand['candidate']['department'].lower() == department.lower()]
        
        return jsonify({
            'success': True,
            'data': pipeline_candidates,
            'summary': {
                'total_candidates': len(pipeline_candidates),
                'ready_now': len([c for c in pipeline_candidates if c['readiness_level'] == 'ready']),
                'developing': len([c for c in pipeline_candidates if c['readiness_level'] == 'developing']),
                'emerging': len([c for c in pipeline_candidates if c['readiness_level'] == 'emerging']),
                'average_readiness_score': sum(c['readiness_score'] for c in pipeline_candidates) / len(pipeline_candidates) if pipeline_candidates else 0
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/development-programs', methods=['GET'])
def get_development_programs():
    """Get leadership development programs"""
    try:
        status = request.args.get('status', 'all')
        
        # Mock development programs data
        programs = [
            {
                'id': 1,
                'name': 'Executive Leadership Program',
                'description': 'Comprehensive 18-month program for senior leadership development',
                'type': 'Leadership',
                'duration_months': 18,
                'status': 'active',
                'start_date': '2024-09-01',
                'end_date': '2026-03-01',
                'participants': [
                    {'name': 'Sarah Chen', 'progress': 85, 'status': 'on_track'},
                    {'name': 'Michael Davis', 'progress': 78, 'status': 'on_track'},
                    {'name': 'Emily Brown', 'progress': 92, 'status': 'excellent'}
                ],
                'curriculum': [
                    'Strategic Leadership',
                    'Change Management',
                    'Financial Acumen',
                    'Executive Communication',
                    'Board Governance'
                ],
                'investment': 240000,
                'completion_rate': 92,
                'satisfaction_score': 4.6,
                'roi_projection': 3.2,
                'facilitator': 'External Leadership Institute'
            },
            {
                'id': 2,
                'name': 'High Potential Leadership Track',
                'description': '12-month accelerated program for emerging leaders',
                'type': 'High Potential',
                'duration_months': 12,
                'status': 'active',
                'start_date': '2025-01-15',
                'end_date': '2026-01-15',
                'participants': [
                    {'name': 'Alex Kumar', 'progress': 65, 'status': 'on_track'},
                    {'name': 'Lisa Wong', 'progress': 70, 'status': 'on_track'},
                    {'name': 'David Kim', 'progress': 58, 'status': 'needs_attention'}
                ],
                'curriculum': [
                    'Leadership Fundamentals',
                    'Team Management',
                    'Project Leadership',
                    'Emotional Intelligence',
                    'Performance Management'
                ],
                'investment': 180000,
                'completion_rate': 88,
                'satisfaction_score': 4.4,
                'roi_projection': 2.8,
                'facilitator': 'Internal HR + External Coach'
            },
            {
                'id': 3,
                'name': 'Future Leaders Initiative',
                'description': '6-month program for identifying and developing emerging talent',
                'type': 'Emerging Talent',
                'duration_months': 6,
                'status': 'completed',
                'start_date': '2025-03-01',
                'end_date': '2025-09-01',
                'participants': [
                    {'name': 'Tom Wilson', 'progress': 100, 'status': 'completed'},
                    {'name': 'Jennifer Lopez', 'progress': 100, 'status': 'completed'},
                    {'name': 'James Taylor', 'progress': 100, 'status': 'completed'}
                ],
                'curriculum': [
                    'Leadership Awareness',
                    'Communication Skills',
                    'Problem Solving',
                    'Team Collaboration',
                    'Professional Development'
                ],
                'investment': 120000,
                'completion_rate': 95,
                'satisfaction_score': 4.5,
                'roi_projection': 2.5,
                'facilitator': 'Internal HR Team'
            }
        ]
        
        # Apply status filter
        if status != 'all':
            programs = [prog for prog in programs if prog['status'] == status]
        
        return jsonify({
            'success': True,
            'data': programs,
            'summary': {
                'total_programs': len(programs),
                'active_programs': len([p for p in programs if p['status'] == 'active']),
                'completed_programs': len([p for p in programs if p['status'] == 'completed']),
                'total_investment': sum(p['investment'] for p in programs),
                'average_satisfaction': sum(p['satisfaction_score'] for p in programs) / len(programs) if programs else 0,
                'average_roi': sum(p['roi_projection'] for p in programs) / len(programs) if programs else 0
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/org-chart', methods=['GET'])
def get_org_chart():
    """Get organizational chart with succession data"""
    try:
        # Mock organizational chart data
        org_chart = {
            'ceo': {
                'position': 'Chief Executive Officer',
                'incumbent': 'Robert Martinez',
                'risk_level': 'high',
                'successors': ['Sarah Chen', 'Michael Davis'],
                'coverage_status': 'covered'
            },
            'vp_level': [
                {
                    'position': 'VP Technology',
                    'incumbent': 'Sarah Chen',
                    'risk_level': 'low',
                    'successors': ['Alex Kumar', 'Lisa Wong'],
                    'coverage_status': 'well_covered'
                },
                {
                    'position': 'VP Operations',
                    'incumbent': 'Michael Davis',
                    'risk_level': 'medium',
                    'successors': ['Tom Wilson'],
                    'coverage_status': 'developing'
                },
                {
                    'position': 'VP Finance',
                    'incumbent': 'Emily Brown',
                    'risk_level': 'medium',
                    'successors': ['David Kim'],
                    'coverage_status': 'developing'
                }
            ],
            'director_level': [
                {
                    'position': 'Engineering Director',
                    'incumbent': 'Alex Kumar',
                    'risk_level': 'low',
                    'successors': ['James Taylor', 'Maria Garcia'],
                    'coverage_status': 'well_covered'
                },
                {
                    'position': 'Marketing Director',
                    'incumbent': 'Jessica Adams',
                    'risk_level': 'high',
                    'successors': [],
                    'coverage_status': 'critical'
                },
                {
                    'position': 'Finance Director',
                    'incumbent': 'David Kim',
                    'risk_level': 'medium',
                    'successors': ['Rachel Green'],
                    'coverage_status': 'developing'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': org_chart
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/analytics', methods=['GET'])
def get_succession_analytics():
    """Get succession planning analytics and insights"""
    try:
        # Mock analytics data
        analytics = {
            'readiness_metrics': {
                'overall_readiness': 75.2,
                'by_department': {
                    'Technology': 85.0,
                    'Finance': 75.0,
                    'Operations': 60.0,
                    'Marketing': 45.0,
                    'HR': 70.0
                },
                'by_level': {
                    'C-Level': 65.0,
                    'VP': 80.0,
                    'Director': 70.0,
                    'Manager': 85.0
                }
            },
            'development_effectiveness': {
                'program_completion_rate': 92,
                'promotion_success_rate': 87,
                'retention_rate_post_development': 94,
                'satisfaction_scores': {
                    'Executive Leadership Program': 4.6,
                    'High Potential Track': 4.4,
                    'Future Leaders Initiative': 4.5
                }
            },
            'risk_assessment': {
                'critical_positions_at_risk': 6,
                'positions_without_successors': 8,
                'upcoming_retirements': [
                    {'name': 'Robert Martinez', 'position': 'CEO', 'retirement_date': '2026-06-30'},
                    {'name': 'Emily Brown', 'position': 'VP Finance', 'retirement_date': '2028-12-31'}
                ],
                'single_point_of_failure': 3
            },
            'financial_metrics': {
                'total_development_investment': 540000,
                'cost_per_successor': 15000,
                'roi_on_development': 3.1,
                'cost_of_external_hiring': 125000,
                'savings_from_internal_promotion': 385000
            },
            'trends': {
                'readiness_improvement': [70, 72, 74, 75, 76],
                'development_participation': [45, 52, 58, 62, 67],
                'succession_coverage': [60, 65, 68, 72, 75]
            },
            'benchmarks': {
                'industry_average_readiness': 68.0,
                'best_in_class_readiness': 85.0,
                'our_performance': 75.2,
                'improvement_opportunity': 9.8
            }
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/create-plan', methods=['POST'])
def create_succession_plan():
    """Create a new succession plan"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['position_id', 'successor_id', 'development_timeline']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock plan creation
        plan = {
            'id': f"SP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'position_id': data['position_id'],
            'successor_id': data['successor_id'],
            'development_timeline': data['development_timeline'],
            'development_goals': data.get('development_goals', []),
            'required_skills': data.get('required_skills', []),
            'mentorship_plan': data.get('mentorship_plan', {}),
            'milestones': data.get('milestones', []),
            'created_by': data.get('created_by', 'System'),
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'expected_completion': data.get('expected_completion'),
            'budget': data.get('budget', 0)
        }
        
        return jsonify({
            'success': True,
            'message': 'Succession plan created successfully',
            'data': plan
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/update-readiness/<int:candidate_id>', methods=['POST'])
def update_readiness(candidate_id):
    """Update candidate readiness assessment"""
    try:
        data = request.get_json()
        
        # Mock readiness update
        assessment = {
            'candidate_id': candidate_id,
            'readiness_score': data.get('readiness_score'),
            'skills_assessment': data.get('skills_assessment', {}),
            'development_progress': data.get('development_progress'),
            'assessor': data.get('assessor', 'System'),
            'assessment_date': datetime.now().isoformat(),
            'next_assessment': data.get('next_assessment'),
            'recommendations': data.get('recommendations', [])
        }
        
        return jsonify({
            'success': True,
            'message': 'Readiness assessment updated successfully',
            'data': assessment
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@succession_planning_bp.route('/api/succession/reports/generate', methods=['POST'])
def generate_succession_report():
    """Generate succession planning reports"""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'readiness_assessment')
        departments = data.get('departments', [])
        include_charts = data.get('include_charts', True)
        
        # Mock report generation
        report = {
            'id': f"SR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': report_type,
            'title': f"Succession Planning {report_type.replace('_', ' ').title()} Report",
            'departments': departments,
            'generated_by': 'System',
            'generated_at': datetime.now().isoformat(),
            'status': 'ready',
            'file_url': f"/reports/succession/{report_type}-{datetime.now().strftime('%Y%m%d')}.pdf",
            'summary': {
                'key_positions_analyzed': 24,
                'succession_candidates': 67,
                'critical_gaps_identified': 6,
                'development_programs_active': 8
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'data': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500