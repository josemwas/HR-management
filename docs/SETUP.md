# HR Management System Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/josemwas/HR-management.git
cd HR-management
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` and set your configuration:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///hr_management.db
```

### 6. Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Create Initial Admin User (Optional)
Open Python shell and create an admin user:
```bash
flask shell
```

```python
from app import db
from app.models import Employee, Department
from datetime import date

# Create a department
dept = Department(name='IT', description='Information Technology')
db.session.add(dept)
db.session.commit()

# Create admin user
admin = Employee(
    employee_id='ADMIN001',
    email='admin@company.com',
    first_name='Admin',
    last_name='User',
    hire_date=date.today(),
    position='System Administrator',
    department_id=dept.id,
    role='admin',
    status='active'
)
admin.set_password('admin123')  # Change this password!
db.session.add(admin)
db.session.commit()
```

### 8. Run the Application
```bash
flask run
```

Or directly:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Testing the API

### Using curl
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "admin123"}'

# Get employees (replace TOKEN with your access token)
curl -X GET http://localhost:5000/api/employees \
  -H "Authorization: Bearer TOKEN"
```

### Using Postman or Insomnia
1. Import the API collection
2. Set base URL: `http://localhost:5000`
3. Login to get access token
4. Use the token in Authorization header for protected endpoints

## Running Tests
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Database Migrations

### Create a new migration
```bash
flask db migrate -m "Description of changes"
```

### Apply migrations
```bash
flask db upgrade
```

### Rollback migration
```bash
flask db downgrade
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Environment Configuration
For production, ensure you:
1. Set `FLASK_ENV=production`
2. Use strong secret keys
3. Use a production database (PostgreSQL, MySQL)
4. Set up proper logging
5. Enable HTTPS
6. Set up a reverse proxy (Nginx, Apache)

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Build and run:
```bash
docker build -t hr-management .
docker run -p 5000:5000 hr-management
```

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database
rm hr_management.db

# Remove migrations
rm -rf migrations/

# Reinitialize
flask db init
flask db migrate
flask db upgrade
```

### Port Already in Use
If port 5000 is already in use:
```bash
# Use a different port
flask run --port 5001
```

### Import Errors
Make sure you've activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Support
For issues and questions, please open an issue on GitHub.
