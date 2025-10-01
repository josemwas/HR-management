# HR Management System

A comprehensive HR Management System designed for organizations from startups to corporates. This system provides complete solutions for managing employees, attendance, leaves, payroll, recruitment, and performance reviews.

## 🚀 Features

### Core Modules

#### 1. Employee Management
- Complete employee profile management
- Department organization
- Role-based access control (Admin, Manager, Employee)
- Employee status tracking (Active, Inactive, Terminated)
- Search and filter capabilities

#### 2. Attendance Tracking
- Real-time check-in/check-out system
- Attendance history and reports
- Multiple status types (Present, Absent, Late, Half-day)
- Date-range filtering

#### 3. Leave Management
- Leave request submission
- Approval workflow (Pending, Approved, Rejected)
- Multiple leave types (Sick, Vacation, Personal, Unpaid)
- Leave balance tracking
- Manager approval interface

#### 4. Payroll Management
- Monthly payroll processing
- Salary components (Basic, Allowances, Deductions, Bonus)
- Payment tracking
- Multiple payment methods
- Payroll history and reports

#### 5. Recruitment System
- Job posting management
- Public job board
- Applicant tracking system
- Application status workflow (Applied, Screening, Interview, Offered, Rejected, Hired)
- Resume and cover letter management

#### 6. Performance Management
- Performance review creation
- Rating system (0-5 scale)
- Goal tracking
- Strengths and improvement areas
- Review history

### Technical Features
- RESTful API architecture
- JWT-based authentication
- Role-based authorization
- SQLite database (easily upgradeable to PostgreSQL/MySQL)
- Database migrations with Flask-Migrate
- CORS enabled for frontend integration
- Comprehensive API documentation

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/josemwas/HR-management.git
   cd HR-management
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

For detailed setup instructions, see [SETUP.md](docs/SETUP.md)

## 📚 API Documentation

Complete API documentation is available in [API.md](docs/API.md)

### Quick API Overview

#### Authentication
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

#### Employees
- `GET /api/employees` - List all employees
- `POST /api/employees` - Create employee
- `GET /api/employees/<id>` - Get employee details
- `PUT /api/employees/<id>` - Update employee
- `DELETE /api/employees/<id>` - Delete employee

#### Attendance
- `POST /api/attendance/check-in` - Check in
- `POST /api/attendance/check-out` - Check out
- `GET /api/attendance` - Get attendance records

#### Leaves
- `GET /api/leaves` - List leave requests
- `POST /api/leaves` - Create leave request
- `POST /api/leaves/<id>/approve` - Approve leave
- `POST /api/leaves/<id>/reject` - Reject leave

#### Payroll
- `GET /api/payroll` - List payroll records
- `POST /api/payroll` - Create payroll record

#### Recruitment
- `GET /api/recruitment/jobs` - List job postings (public)
- `POST /api/recruitment/apply` - Apply for job (public)
- `GET /api/recruitment/applicants` - List applicants

#### Performance
- `GET /api/performance` - List performance reviews
- `POST /api/performance` - Create performance review

## 🏗️ Project Structure

```
HR-management/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── employee.py
│   │   ├── department.py
│   │   ├── attendance.py
│   │   ├── leave.py
│   │   ├── payroll.py
│   │   ├── recruitment.py
│   │   └── performance.py
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── attendance.py
│   │   ├── leaves.py
│   │   ├── payroll.py
│   │   ├── recruitment.py
│   │   └── performance.py
│   └── utils/               # Utility functions
├── config/
│   └── config.py            # Configuration settings
├── docs/
│   ├── API.md               # API documentation
│   └── SETUP.md             # Setup guide
├── tests/                   # Test files
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore file
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
└── README.md               # This file
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_employees.py
```

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker
```bash
docker build -t hr-management .
docker run -p 5000:5000 hr-management
```

## 🔒 Security

- JWT-based authentication
- Password hashing with Werkzeug
- Role-based access control
- CORS protection
- Environment-based configuration

## 🌟 Use Cases

### For Startups
- Quick setup and deployment
- All-in-one HR solution
- Cost-effective
- Scalable architecture

### For Small/Medium Businesses
- Complete HR workflow automation
- Employee self-service portal
- Manager approval workflows
- Comprehensive reporting

### For Enterprises
- Scalable to thousands of employees
- Department-based organization
- Role-based permissions
- API-first architecture for integrations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- Jose Mwas - Initial work - [josemwas](https://github.com/josemwas)

## 🙏 Acknowledgments

- Flask framework and community
- All contributors and users

## 📧 Support

For support, email support@example.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Frontend web application (React/Vue.js)
- [ ] Mobile application (React Native)
- [ ] Advanced reporting and analytics
- [ ] Email notifications
- [ ] Document management
- [ ] Time tracking integration
- [ ] Benefits management
- [ ] Training and development module
- [ ] Multi-language support
- [ ] Advanced security features (2FA)

## 📊 Status

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask Version](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

Made with ❤️ by [josemwas](https://github.com/josemwas)