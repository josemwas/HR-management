"""
Tests for AI Assistant module
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    yield app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


def test_ai_assistant_blueprint_registered(app):
    """Test that AI assistant blueprint is registered"""
    assert 'ai_assistant' in app.blueprints
    print("✅ AI assistant blueprint is registered")


def test_ai_endpoints_exist(app):
    """Test that AI endpoints are registered"""
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    expected_endpoints = [
        '/api/ai/chat',
        '/api/ai/performance-analysis/<int:employee_id>',
        '/api/ai/training-recommendations/<int:employee_id>',
        '/api/ai/attrition-risk/<int:employee_id>',
        '/api/ai/succession-recommendations',
        '/api/ai/recruitment-forecast',
        '/api/ai/insights/dashboard',
        '/api/ai/ask'
    ]
    
    for endpoint in expected_endpoints:
        assert endpoint in routes, f"Endpoint {endpoint} not found"
    
    print(f"✅ All {len(expected_endpoints)} AI endpoints are registered")


def test_ai_chat_endpoint_without_auth(client):
    """Test AI chat endpoint requires authentication"""
    response = client.post('/api/ai/chat', json={'question': 'test'})
    assert response.status_code == 401
    print("✅ AI chat endpoint properly requires authentication")


def test_ai_performance_analysis_endpoint_without_auth(client):
    """Test performance analysis endpoint requires authentication"""
    response = client.get('/api/ai/performance-analysis/1')
    assert response.status_code == 401
    print("✅ Performance analysis endpoint properly requires authentication")


def test_ai_training_recommendations_endpoint_without_auth(client):
    """Test training recommendations endpoint requires authentication"""
    response = client.get('/api/ai/training-recommendations/1')
    assert response.status_code == 401
    print("✅ Training recommendations endpoint properly requires authentication")


def test_ai_dashboard_insights_endpoint_without_auth(client):
    """Test dashboard insights endpoint requires authentication"""
    response = client.get('/api/ai/insights/dashboard')
    assert response.status_code == 401
    print("✅ Dashboard insights endpoint properly requires authentication")


def test_ai_natural_language_query_endpoint_without_auth(client):
    """Test natural language query endpoint requires authentication"""
    response = client.post('/api/ai/ask', json={'query': 'test'})
    assert response.status_code == 401
    print("✅ Natural language query endpoint properly requires authentication")


def test_api_info_includes_ai_features(client):
    """Test that API info endpoint includes AI features"""
    response = client.get('/api')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'features' in data
    
    ai_features = [
        'AI-powered insights and recommendations',
        'Intelligent chatbot assistance',
        'Predictive attrition analysis',
        'Automated succession planning'
    ]
    
    for feature in ai_features:
        assert feature in data['features'], f"AI feature '{feature}' not in API info"
    
    assert 'ai_assistant' in data['endpoints']
    print("✅ API info includes all AI features")


def test_ai_assistant_page_route_exists(client):
    """Test that AI assistant page route exists"""
    response = client.get('/ai-assistant')
    # Should return 200 or 302 (redirect), but not 404
    assert response.status_code != 404
    print("✅ AI assistant page route exists")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
