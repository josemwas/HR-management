"""
Example script demonstrating how to use the HR Management System API
This script shows common operations using the requests library

Requirements: pip install requests

Usage: python examples/api_usage_example.py
"""
import requests
from datetime import date, timedelta
import json

# Base URL of the API
BASE_URL = "http://localhost:5000/api"

class HRClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        
    def login(self, email, password):
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            print(f"✓ Logged in as {data['employee']['first_name']} {data['employee']['last_name']}")
            return data
        else:
            print(f"✗ Login failed: {response.json()}")
            return None
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def get_employees(self, page=1, per_page=10):
        """Get list of employees"""
        response = requests.get(
            f"{self.base_url}/employees",
            headers=self.get_headers(),
            params={"page": page, "per_page": per_page}
        )
        return response.json()
    
    def create_employee(self, employee_data):
        """Create a new employee"""
        response = requests.post(
            f"{self.base_url}/employees",
            headers=self.get_headers(),
            json=employee_data
        )
        return response.json()
    
    def check_in(self):
        """Check in for the day"""
        response = requests.post(
            f"{self.base_url}/attendance/check-in",
            headers=self.get_headers()
        )
        return response.json()
    
    def request_leave(self, leave_data):
        """Request leave"""
        response = requests.post(
            f"{self.base_url}/leaves",
            headers=self.get_headers(),
            json=leave_data
        )
        return response.json()
    
    def get_job_postings(self):
        """Get public job postings"""
        response = requests.get(f"{self.base_url}/recruitment/jobs")
        return response.json()


def main():
    """Demonstrate various API operations"""
    
    print("=" * 60)
    print("HR Management System API Usage Example")
    print("=" * 60)
    print()
    
    # Initialize client
    client = HRClient(BASE_URL)
    
    # 1. Login as admin
    print("1. Login as Admin")
    print("-" * 60)
    login_result = client.login("admin@company.com", "password123")
    if not login_result:
        print("Failed to login. Make sure the server is running and data is initialized.")
        return
    print()
    
    # 2. Get employees
    print("2. Get Employees")
    print("-" * 60)
    employees = client.get_employees(per_page=5)
    print(f"Total employees: {employees['total']}")
    print(f"Showing {len(employees['employees'])} employees:")
    for emp in employees['employees']:
        print(f"  - {emp['first_name']} {emp['last_name']} ({emp['position']})")
    print()
    
    # 3. Check in
    print("3. Check In")
    print("-" * 60)
    checkin = client.check_in()
    if 'error' in checkin:
        print(f"Note: {checkin['error']}")
    else:
        print(f"✓ Checked in at {checkin.get('check_in', 'N/A')}")
    print()
    
    # 4. Request leave
    print("4. Request Leave")
    print("-" * 60)
    leave_request = {
        "leave_type": "vacation",
        "start_date": str(date.today() + timedelta(days=30)),
        "end_date": str(date.today() + timedelta(days=34)),
        "days": 5,
        "reason": "Family vacation"
    }
    leave = client.request_leave(leave_request)
    print(f"✓ Leave requested: {leave.get('leave_type', 'N/A')} from {leave.get('start_date', 'N/A')} to {leave.get('end_date', 'N/A')}")
    print()
    
    # 5. Get job postings
    print("5. Get Job Postings (Public)")
    print("-" * 60)
    jobs = client.get_job_postings()
    print(f"Available positions: {len(jobs)}")
    for job in jobs:
        print(f"  - {job['title']} ({job['location']}) - {job['employment_type']}")
    print()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
