#!/usr/bin/env python3
"""
Test script to check authentication and RBAC functionality
"""
import requests
import json

def test_login_and_rbac():
    base_url = "http://127.0.0.1:5000"
    
    try:
        print("Testing Flask app accessibility...")
        
        # Test if the app is accessible
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Homepage status: {response.status_code}")
        
        # Test login page
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"Login page status: {response.status_code}")
        
        # Test roles page (should redirect to login if not authenticated)
        response = requests.get(f"{base_url}/roles", timeout=5)
        print(f"Roles page status: {response.status_code}")
        
        # Test settings page
        response = requests.get(f"{base_url}/settings", timeout=5)
        print(f"Settings page status: {response.status_code}")
        
        # Test API login
        print("\nTesting authentication...")
        login_data = {
            "email": "admin@acme-corp.com",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        print(f"API login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"Authentication: SUCCESS - Got token")
            
            # Test RBAC API with token
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test permissions endpoint
            response = requests.get(f"{base_url}/api/rbac/permissions", 
                                  headers=headers, timeout=5)
            print(f"RBAC permissions API status: {response.status_code}")
            
            # Test roles endpoint
            response = requests.get(f"{base_url}/api/rbac/roles", 
                                  headers=headers, timeout=5)
            print(f"RBAC roles API status: {response.status_code}")
            
            # Test settings endpoint
            response = requests.get(f"{base_url}/api/rbac/settings", 
                                  headers=headers, timeout=5)
            print(f"RBAC settings API status: {response.status_code}")
            
        else:
            print(f"Authentication: FAILED - {response.text}")
        
        print("\n✅ All tests completed")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app - make sure it's running on http://127.0.0.1:5000")
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Flask app may be unresponsive")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_login_and_rbac()