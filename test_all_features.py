#!/usr/bin/env python3
"""
Test all HR feature APIs to see which ones are working
"""
import requests
import json

def test_all_apis():
    base_url = "http://127.0.0.1:5000"
    
    # First login to get token
    print("🔐 Testing Authentication...")
    login_data = {
        "email": "admin@acme-corp.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
            
        token_data = response.json()
        token = token_data.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print(f"✅ Login successful - Got token")
        
        # Test core HR APIs
        apis_to_test = [
            ("/api/employees", "Employee Management"),
            ("/api/attendance", "Attendance Tracking"),
            ("/api/leaves", "Leave Management"), 
            ("/api/payroll", "Payroll Management"),
            ("/api/performance", "Performance Reviews"),
            ("/api/recruitment/jobs", "Recruitment"),
            ("/api/training/programs", "Training Programs"),
            ("/api/rbac/roles", "Roles & Permissions"),
            ("/api/rbac/settings", "Organization Settings")
        ]
        
        print("\n🔧 Testing HR Feature APIs...")
        working_apis = []
        broken_apis = []
        
        for api_path, feature_name in apis_to_test:
            try:
                response = requests.get(f"{base_url}{api_path}", 
                                      headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {feature_name}: Working ({response.status_code})")
                    working_apis.append(feature_name)
                else:
                    print(f"❌ {feature_name}: Error ({response.status_code})")
                    broken_apis.append((feature_name, response.status_code))
                    
            except Exception as e:
                print(f"❌ {feature_name}: Exception - {str(e)}")
                broken_apis.append((feature_name, f"Exception: {str(e)}"))
        
        print(f"\n📊 Summary:")
        print(f"✅ Working APIs: {len(working_apis)}")
        print(f"❌ Broken APIs: {len(broken_apis)}")
        
        if broken_apis:
            print("\n🔍 Issues found:")
            for api, error in broken_apis:
                print(f"  - {api}: {error}")
        else:
            print("\n🎉 All APIs are working correctly!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app - make sure it's running")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_all_apis()