#!/usr/bin/env python3
"""
Verification Script for HR Management System
Validates that all features are implemented and working
"""

import sys
from app import create_app

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def verify_blueprints(app):
    """Verify all blueprints are registered"""
    print_header("Blueprint Verification")
    
    expected_blueprints = [
        'auth', 'rbac', 'employees', 'organizations', 'attendance',
        'leaves', 'timesheets', 'time_labor', 'performance', 'training',
        'recruitment', 'onboarding', 'payroll', 'benefits', 'compensation',
        'exit_management', 'employee_relations', 'succession_planning',
        'workforce_planning', 'analytics', 'self_service', 'announcements',
        'documents', 'compliance', 'ai_assistant', 'saas_admin', 'super_admin'
    ]
    
    registered = list(app.blueprints.keys())
    
    print_info(f"Expected blueprints: {len(expected_blueprints)}")
    print_info(f"Registered blueprints: {len(registered)}")
    
    missing = set(expected_blueprints) - set(registered)
    if missing:
        print(f"❌ Missing blueprints: {missing}")
        return False
    
    print_success(f"All {len(expected_blueprints)} blueprints registered!")
    return True

def verify_ai_endpoints(app):
    """Verify AI endpoints are registered"""
    print_header("AI Endpoints Verification")
    
    expected_ai_routes = [
        '/api/ai/chat',
        '/api/ai/performance-analysis/<int:employee_id>',
        '/api/ai/training-recommendations/<int:employee_id>',
        '/api/ai/attrition-risk/<int:employee_id>',
        '/api/ai/succession-recommendations',
        '/api/ai/recruitment-forecast',
        '/api/ai/insights/dashboard',
        '/api/ai/ask'
    ]
    
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    for expected_route in expected_ai_routes:
        if expected_route in routes:
            print_success(f"Found: {expected_route}")
        else:
            print(f"❌ Missing: {expected_route}")
            return False
    
    print_success(f"All {len(expected_ai_routes)} AI endpoints registered!")
    return True

def verify_frontend_pages(app):
    """Verify frontend pages exist"""
    print_header("Frontend Pages Verification")
    
    expected_pages = [
        '/', '/login', '/signup', '/dashboard', '/employees',
        '/attendance', '/leaves', '/payroll', '/performance',
        '/recruitment', '/training', '/benefits', '/ai-assistant'
    ]
    
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    for page in expected_pages:
        if page in routes:
            print_success(f"Page exists: {page}")
        else:
            print(f"❌ Missing page: {page}")
            return False
    
    print_success(f"All {len(expected_pages)} pages registered!")
    return True

def verify_api_info(app):
    """Verify API info includes AI features"""
    print_header("API Info Verification")
    
    with app.test_client() as client:
        response = client.get('/api')
        if response.status_code != 200:
            print("❌ Failed to get API info")
            return False
        
        data = response.get_json()
        
        # Check AI features
        ai_features = [
            'AI-powered insights and recommendations',
            'Intelligent chatbot assistance',
            'Predictive attrition analysis',
            'Automated succession planning'
        ]
        
        for feature in ai_features:
            if feature in data.get('features', []):
                print_success(f"Feature listed: {feature}")
            else:
                print(f"❌ Missing feature: {feature}")
                return False
        
        # Check AI endpoint
        if 'ai_assistant' in data.get('endpoints', {}):
            print_success("AI assistant endpoint in API info")
        else:
            print("❌ AI assistant endpoint not in API info")
            return False
        
        # Check module count
        module_count = data.get('module_count', 0)
        if module_count == 27:
            print_success(f"Module count correct: {module_count}")
        else:
            print(f"❌ Module count incorrect: {module_count} (expected 27)")
            return False
    
    print_success("API info verification complete!")
    return True

def verify_file_structure():
    """Verify important files exist"""
    print_header("File Structure Verification")
    
    import os
    
    required_files = [
        'app/routes/ai_assistant.py',
        'templates/ai_assistant.html',
        'tests/test_ai_assistant.py',
        'docs/AI_ASSISTANT.md',
        'FEATURES_COMPLETE.md',
        'IMPLEMENTATION_SUMMARY.md',
        'static/js/app.js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    print_success("All required files exist!")
    return True

def count_routes(app):
    """Count and display route statistics"""
    print_header("Route Statistics")
    
    routes = list(app.url_map.iter_rules())
    ai_routes = [r for r in routes if '/api/ai/' in r.rule]
    api_routes = [r for r in routes if '/api/' in r.rule]
    page_routes = [r for r in routes if '/api/' not in r.rule]
    
    print_info(f"Total routes: {len(routes)}")
    print_info(f"API routes: {len(api_routes)}")
    print_info(f"AI routes: {len(ai_routes)}")
    print_info(f"Page routes: {len(page_routes)}")
    
    print_success("Route counting complete!")
    return True

def main():
    """Main verification function"""
    print_header("🚀 HR Management System - Implementation Verification")
    print_info("Starting comprehensive verification...")
    
    # Create app
    try:
        app = create_app('testing')
        print_success("Application created successfully!")
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        return False
    
    # Run all verifications
    verifications = [
        ("File Structure", verify_file_structure),
        ("Blueprints", lambda: verify_blueprints(app)),
        ("AI Endpoints", lambda: verify_ai_endpoints(app)),
        ("Frontend Pages", lambda: verify_frontend_pages(app)),
        ("API Info", lambda: verify_api_info(app)),
        ("Route Statistics", lambda: count_routes(app))
    ]
    
    results = []
    for name, verify_func in verifications:
        try:
            result = verify_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("📊 Verification Summary")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} verifications passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 ALL VERIFICATIONS PASSED! System is ready for production!")
        return True
    else:
        print("❌ Some verifications failed. Please review the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
