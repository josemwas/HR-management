"""
AI Assistant Module for HR Management System
Provides intelligent recommendations and insights using AI/ML capabilities
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import random

ai_assistant_bp = Blueprint('ai_assistant', __name__)


class AIAssistant:
    """AI Assistant service for HR recommendations and insights"""
    
    @staticmethod
    def analyze_employee_performance(employee_data):
        """Analyze employee performance and provide recommendations"""
        # Mock AI analysis
        performance_score = random.uniform(3.5, 5.0)
        
        recommendations = []
        if performance_score < 4.0:
            recommendations.extend([
                "Consider enrolling in leadership training programs",
                "Schedule monthly one-on-one coaching sessions",
                "Set clear, measurable goals for next quarter"
            ])
        elif performance_score < 4.5:
            recommendations.extend([
                "Ready for stretch assignments and new challenges",
                "Consider for cross-functional project leadership",
                "Explore mentorship opportunities"
            ])
        else:
            recommendations.extend([
                "Excellent candidate for promotion consideration",
                "Identify as high-potential talent for succession planning",
                "Consider for advanced leadership development programs"
            ])
        
        return {
            'performance_score': round(performance_score, 2),
            'performance_level': 'Exceptional' if performance_score >= 4.5 else 'Strong' if performance_score >= 4.0 else 'Developing',
            'recommendations': recommendations,
            'confidence': random.uniform(0.85, 0.98)
        }
    
    @staticmethod
    def suggest_training_programs(employee_profile):
        """Suggest relevant training programs based on employee profile"""
        skill_areas = [
            {
                'area': 'Technical Skills',
                'programs': [
                    'Advanced Python Programming',
                    'Cloud Architecture Certification',
                    'AI/ML Fundamentals',
                    'DevOps Best Practices'
                ]
            },
            {
                'area': 'Leadership & Management',
                'programs': [
                    'Executive Leadership Program',
                    'Team Management Essentials',
                    'Strategic Decision Making',
                    'Change Management'
                ]
            },
            {
                'area': 'Soft Skills',
                'programs': [
                    'Effective Communication',
                    'Emotional Intelligence',
                    'Conflict Resolution',
                    'Time Management Mastery'
                ]
            }
        ]
        
        # Select 2-3 relevant programs based on role/level
        suggested = random.sample(skill_areas, k=2)
        
        return {
            'suggested_programs': suggested,
            'priority': 'High' if random.random() > 0.5 else 'Medium',
            'estimated_duration': f"{random.randint(20, 80)} hours",
            'expected_impact': 'Significant skill enhancement and career growth'
        }
    
    @staticmethod
    def predict_attrition_risk(employee_data):
        """Predict employee attrition risk"""
        risk_score = random.uniform(0, 1)
        
        risk_factors = []
        if risk_score > 0.7:
            risk_factors.extend([
                'Below market compensation',
                'Limited career growth opportunities',
                'High workload indicators',
                'Low engagement scores'
            ])
        elif risk_score > 0.4:
            risk_factors.extend([
                'Average satisfaction levels',
                'Moderate career advancement pace',
                'Normal workload balance'
            ])
        else:
            risk_factors.extend([
                'High engagement scores',
                'Competitive compensation',
                'Strong career trajectory'
            ])
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low',
            'risk_factors': risk_factors[:3],
            'retention_actions': [
                'Schedule career development conversation',
                'Review compensation against market rates',
                'Provide recognition and growth opportunities'
            ] if risk_score > 0.5 else []
        }
    
    @staticmethod
    def recommend_succession_candidates(position_data):
        """Recommend candidates for succession planning"""
        candidates = [
            {
                'name': 'Sarah Johnson',
                'current_role': 'Senior Manager',
                'readiness_score': 0.92,
                'strengths': ['Strategic thinking', 'Team leadership', 'Domain expertise'],
                'development_areas': ['Executive presence', 'Board-level communication'],
                'timeline': '6 months'
            },
            {
                'name': 'Michael Chen',
                'current_role': 'Director of Operations',
                'readiness_score': 0.85,
                'strengths': ['Operational excellence', 'Change management', 'Financial acumen'],
                'development_areas': ['Strategic planning', 'Stakeholder management'],
                'timeline': '12 months'
            },
            {
                'name': 'Emily Rodriguez',
                'current_role': 'VP Product',
                'readiness_score': 0.88,
                'strengths': ['Innovation', 'Customer focus', 'Cross-functional leadership'],
                'development_areas': ['P&L management', 'M&A experience'],
                'timeline': '9 months'
            }
        ]
        
        return {
            'recommended_candidates': sorted(candidates, key=lambda x: x['readiness_score'], reverse=True),
            'succession_strategy': 'Develop internal pipeline while maintaining external search readiness',
            'confidence': 0.89
        }
    
    @staticmethod
    def analyze_recruitment_needs(workforce_data):
        """Analyze and predict recruitment needs"""
        return {
            'urgent_positions': [
                {'role': 'Senior Software Engineer', 'count': 5, 'priority': 'Critical', 'time_to_fill': '45 days'},
                {'role': 'Product Manager', 'count': 2, 'priority': 'High', 'time_to_fill': '60 days'},
                {'role': 'Data Scientist', 'count': 3, 'priority': 'High', 'time_to_fill': '50 days'}
            ],
            'forecasted_needs': [
                {'quarter': 'Q2 2026', 'estimated_hires': 15, 'focus_areas': ['Engineering', 'Sales']},
                {'quarter': 'Q3 2026', 'estimated_hires': 20, 'focus_areas': ['Product', 'Marketing']},
                {'quarter': 'Q4 2026', 'estimated_hires': 12, 'focus_areas': ['Operations', 'Finance']}
            ],
            'market_insights': {
                'competition_level': 'High',
                'average_time_to_fill': '52 days',
                'recommended_sourcing': ['LinkedIn Recruiter', 'Tech conferences', 'Employee referrals']
            }
        }
    
    @staticmethod
    def generate_chatbot_response(question, context):
        """Generate AI chatbot response to HR queries"""
        question_lower = question.lower()
        
        # Simple pattern matching for common HR queries
        if 'leave' in question_lower or 'time off' in question_lower:
            return {
                'response': "I can help you with leave requests! You have several leave types available: Sick Leave, Vacation, Personal Leave, and Unpaid Leave. To request leave, go to the Leaves section and click 'Request Leave'. Your manager will be notified for approval.",
                'category': 'leave_management',
                'helpful_links': ['/leaves', '/leave-balance']
            }
        elif 'payroll' in question_lower or 'salary' in question_lower:
            return {
                'response': "For payroll inquiries, you can view your payment history and pay stubs in the Payroll section. If you have questions about your salary or deductions, please contact HR at hr@company.com or your manager.",
                'category': 'payroll',
                'helpful_links': ['/payroll', '/compensation']
            }
        elif 'training' in question_lower or 'course' in question_lower:
            return {
                'response': "We offer various training programs to support your professional development! Visit the Training section to see available courses, enroll in programs, and track your learning progress. I can also recommend personalized training based on your role.",
                'category': 'training',
                'helpful_links': ['/training', '/training/recommendations']
            }
        elif 'performance' in question_lower or 'review' in question_lower:
            return {
                'response': "Performance reviews help you track your progress and set goals. You can view your past reviews, current goals, and feedback in the Performance section. Reviews are typically conducted quarterly and annually.",
                'category': 'performance',
                'helpful_links': ['/performance', '/goals']
            }
        elif 'benefit' in question_lower or 'insurance' in question_lower:
            return {
                'response': "Our benefits package includes health insurance, dental, vision, 401(k), and more! Check the Benefits section for details on your enrollment, coverage, and how to make changes during open enrollment periods.",
                'category': 'benefits',
                'helpful_links': ['/benefits', '/benefits/enrollment']
            }
        else:
            return {
                'response': f"I'm here to help with HR questions! I can assist with: Leave requests, Payroll information, Training programs, Performance reviews, Benefits enrollment, and general HR policies. Could you please rephrase your question or be more specific about what you need help with?",
                'category': 'general',
                'helpful_links': ['/self-service', '/help']
            }


@ai_assistant_bp.route('/api/ai/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """AI-powered chatbot for employee queries"""
    try:
        data = request.json
        question = data.get('question', '')
        context = data.get('context', {})
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        response = AIAssistant.generate_chatbot_response(question, context)
        
        return jsonify({
            'success': True,
            'data': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/performance-analysis/<int:employee_id>', methods=['GET'])
@jwt_required()
def analyze_performance(employee_id):
    """Get AI-powered performance analysis for an employee"""
    try:
        # In production, fetch actual employee data
        employee_data = {'id': employee_id}
        
        analysis = AIAssistant.analyze_employee_performance(employee_data)
        
        return jsonify({
            'success': True,
            'employee_id': employee_id,
            'analysis': analysis,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/training-recommendations/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_training_recommendations(employee_id):
    """Get AI-powered training recommendations"""
    try:
        employee_profile = {'id': employee_id}
        
        recommendations = AIAssistant.suggest_training_programs(employee_profile)
        
        return jsonify({
            'success': True,
            'employee_id': employee_id,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/attrition-risk/<int:employee_id>', methods=['GET'])
@jwt_required()
def check_attrition_risk(employee_id):
    """Predict employee attrition risk"""
    try:
        employee_data = {'id': employee_id}
        
        risk_analysis = AIAssistant.predict_attrition_risk(employee_data)
        
        return jsonify({
            'success': True,
            'employee_id': employee_id,
            'risk_analysis': risk_analysis,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/succession-recommendations', methods=['POST'])
@jwt_required()
def get_succession_recommendations():
    """Get AI-powered succession planning recommendations"""
    try:
        data = request.json
        position_data = data.get('position', {})
        
        recommendations = AIAssistant.recommend_succession_candidates(position_data)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/recruitment-forecast', methods=['GET'])
@jwt_required()
def get_recruitment_forecast():
    """Get AI-powered recruitment needs forecast"""
    try:
        workforce_data = {}  # In production, fetch actual workforce data
        
        forecast = AIAssistant.analyze_recruitment_needs(workforce_data)
        
        return jsonify({
            'success': True,
            'forecast': forecast,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/insights/dashboard', methods=['GET'])
@jwt_required()
def get_ai_dashboard_insights():
    """Get comprehensive AI insights for dashboard"""
    try:
        insights = {
            'key_insights': [
                {
                    'title': 'High Attrition Risk Detected',
                    'description': '5 employees showing high attrition risk indicators',
                    'severity': 'high',
                    'action': 'Review retention strategies',
                    'link': '/ai/attrition-analysis'
                },
                {
                    'title': 'Training Gaps Identified',
                    'description': 'AI/ML skills gap affecting 15 employees in Engineering',
                    'severity': 'medium',
                    'action': 'Launch upskilling program',
                    'link': '/training/recommendations'
                },
                {
                    'title': 'Succession Planning Alert',
                    'description': '3 key positions lack ready successors',
                    'severity': 'medium',
                    'action': 'Develop succession pipeline',
                    'link': '/succession-planning'
                }
            ],
            'recommendations': [
                'Consider hiring 5 senior engineers in Q1 2026',
                'Launch leadership development program for 10 high-potential employees',
                'Review compensation for top performers to reduce attrition risk'
            ],
            'predictive_metrics': {
                'attrition_rate_forecast': '12.5%',
                'time_to_fill_average': '45 days',
                'training_completion_rate': '87%',
                'performance_trend': 'Improving'
            }
        }
        
        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/api/ai/ask', methods=['POST'])
@jwt_required()
def natural_language_query():
    """Process natural language queries about HR data"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Simple NLP processing (in production, use actual NLP/LLM)
        query_lower = query.lower()
        
        if 'how many' in query_lower and 'employee' in query_lower:
            response = {
                'answer': 'We currently have 247 active employees across 8 departments.',
                'data': {'total_employees': 247, 'departments': 8},
                'visualization': 'bar_chart'
            }
        elif 'attrition' in query_lower or 'turnover' in query_lower:
            response = {
                'answer': 'Current attrition rate is 11.3% annually, which is below industry average of 13.5%.',
                'data': {'current_rate': 11.3, 'industry_avg': 13.5, 'target': 10.0},
                'visualization': 'line_chart'
            }
        elif 'training' in query_lower and 'completion' in query_lower:
            response = {
                'answer': 'Training completion rate is 87% across all programs, with leadership programs at 94%.',
                'data': {'overall': 87, 'leadership': 94, 'technical': 82, 'soft_skills': 89},
                'visualization': 'pie_chart'
            }
        else:
            response = {
                'answer': f"I found relevant information about: {query}. Could you be more specific about what metrics or insights you're looking for?",
                'suggestions': [
                    'Show employee headcount by department',
                    'What is the current attrition rate?',
                    'Training completion statistics',
                    'Performance review summary'
                ]
            }
        
        return jsonify({
            'success': True,
            'query': query,
            'response': response,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
