# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (1 minute)
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Initialize Database with Sample Data (1 minute)
```bash
# This creates the database and adds sample employees, departments, etc.
python init_sample_data.py
```

### 3. Start the Server (1 minute)
```bash
python run.py
```

The API is now running at `http://localhost:5000`

### 4. Test the API (2 minutes)

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "password123"}'
```

This returns an access token. Copy it!

#### Get Employees
```bash
curl http://localhost:5000/api/employees \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Check Available Endpoints
```bash
curl http://localhost:5000/
```

## Sample Credentials

After running `init_sample_data.py`, you can login with:

**Admin User:**
- Email: `admin@company.com`
- Password: `password123`
- Role: admin

**Manager User:**
- Email: `john.manager@company.com`
- Password: `password123`
- Role: manager

**Employee User:**
- Email: `jane.dev@company.com`
- Password: `password123`
- Role: employee

## Common Operations

### Check-in for the day
```bash
TOKEN="your_access_token"
curl -X POST http://localhost:5000/api/attendance/check-in \
  -H "Authorization: Bearer $TOKEN"
```

### Request leave
```bash
curl -X POST http://localhost:5000/api/leaves \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "vacation",
    "start_date": "2024-05-01",
    "end_date": "2024-05-05",
    "days": 5,
    "reason": "Family vacation"
  }'
```

### View job postings (no auth needed)
```bash
curl http://localhost:5000/api/recruitment/jobs
```

### Apply for a job (no auth needed)
```bash
curl -X POST http://localhost:5000/api/recruitment/apply \
  -H "Content-Type: application/json" \
  -d '{
    "job_posting_id": 1,
    "first_name": "John",
    "last_name": "Applicant",
    "email": "john@example.com",
    "phone": "1234567890",
    "applied_date": "2024-03-01"
  }'
```

## Testing

Run all tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Next Steps

1. Read the [API Documentation](docs/API.md) for all endpoints
2. Review [Features Documentation](docs/FEATURES.md) for detailed capabilities
3. Check [Setup Guide](docs/SETUP.md) for production deployment
4. Customize the system for your organization

## Troubleshooting

### Problem: Import errors
**Solution:** Make sure virtual environment is activated
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Problem: Database errors
**Solution:** Reinitialize the database
```bash
python init_sample_data.py
```

### Problem: Port 5000 already in use
**Solution:** Use a different port
```bash
flask run --port 5001
```

## Production Checklist

Before deploying to production:
- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY in .env
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure backup strategy
- [ ] Set up monitoring
- [ ] Review security settings
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx, Apache)

## Getting Help

- **Documentation:** Check the `docs/` folder
- **Issues:** Open an issue on GitHub
- **API Reference:** See `docs/API.md`
- **Features:** See `docs/FEATURES.md`

## Project Structure

```
HR-management/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   └── utils/           # Utility functions
├── config/              # Configuration
├── docs/                # Documentation
├── tests/               # Test files
├── run.py              # Application entry point
└── init_sample_data.py # Sample data script
```

## Key Technologies

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Pytest** - Testing framework

---

🎉 **You're all set!** Start building your HR management solution.
