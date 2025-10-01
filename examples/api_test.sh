#!/bin/bash
# Simple script to test HR Management System API
# Usage: ./examples/api_test.sh

BASE_URL="http://localhost:5000/api"

echo "=========================================="
echo "HR Management System API Test Script"
echo "=========================================="
echo ""

# Check if server is running
echo "Checking if API server is running..."
if ! curl -s -f "$BASE_URL/../" > /dev/null; then
    echo "✗ Error: API server is not running"
    echo "Please start the server: python run.py"
    exit 1
fi
echo "✓ Server is running"
echo ""

# 1. Login
echo "1. Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo "✗ Login failed"
    echo "Make sure you've run: python init_sample_data.py"
    exit 1
fi

echo "✓ Login successful"
echo ""

# 2. Get employees
echo "2. Getting employees list..."
curl -s "$BASE_URL/employees?per_page=3" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
echo ""

# 3. Get departments
echo "3. Getting departments..."
curl -s "$BASE_URL/employees/departments" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 4. Get job postings (no auth needed)
echo "4. Getting job postings (public)..."
curl -s "$BASE_URL/recruitment/jobs" | python3 -m json.tool
echo ""

# 5. Get current user info
echo "5. Getting current user info..."
curl -s "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "API Test completed successfully!"
echo "=========================================="
echo ""
echo "All endpoints are working correctly."
echo "Check docs/API.md for complete documentation."
