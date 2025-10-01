import pytest

def test_login_success(client, sample_employee):
    """Test successful login"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'employee' in data

def test_login_invalid_credentials(client, sample_employee):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_login_missing_fields(client):
    """Test login with missing fields"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 400

def test_get_current_employee(client, auth_headers):
    """Test getting current employee info"""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'test@example.com'

def test_get_current_employee_no_auth(client):
    """Test getting current employee without authentication"""
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_change_password(client, auth_headers):
    """Test changing password"""
    response = client.post('/api/auth/change-password', 
                          headers=auth_headers,
                          json={
                              'old_password': 'password123',
                              'new_password': 'newpassword123'
                          })
    assert response.status_code == 200

def test_change_password_invalid_old(client, auth_headers):
    """Test changing password with invalid old password"""
    response = client.post('/api/auth/change-password',
                          headers=auth_headers,
                          json={
                              'old_password': 'wrongpassword',
                              'new_password': 'newpassword123'
                          })
    assert response.status_code == 401
