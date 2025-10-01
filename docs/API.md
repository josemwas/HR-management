# HR Management System API Documentation

## Overview
This is a comprehensive HR Management System API built with Flask, designed to handle all HR operations from employee management to payroll processing.

## Base URL
```
http://localhost:5000/api
```

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication (`/api/auth`)

#### POST /api/auth/login
Login and receive JWT tokens.
```json
Request:
{
  "email": "user@example.com",
  "password": "password"
}

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "employee": {...}
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

#### GET /api/auth/me
Get current authenticated employee information.

#### POST /api/auth/change-password
Change employee password.

### Employees (`/api/employees`)

#### GET /api/employees
Get all employees with pagination and filters.
- Query params: `page`, `per_page`, `status`, `department_id`

#### GET /api/employees/<id>
Get employee by ID.

#### POST /api/employees
Create new employee.
```json
{
  "employee_id": "EMP001",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "hire_date": "2024-01-01",
  "position": "Software Engineer",
  "department_id": 1,
  "salary": 75000,
  "password": "initialPassword"
}
```

#### PUT /api/employees/<id>
Update employee information.

#### DELETE /api/employees/<id>
Delete employee.

#### GET /api/employees/departments
Get all departments.

#### POST /api/employees/departments
Create new department.

### Attendance (`/api/attendance`)

#### GET /api/attendance
Get attendance records with filters.
- Query params: `employee_id`, `start_date`, `end_date`

#### GET /api/attendance/<id>
Get attendance by ID.

#### POST /api/attendance/check-in
Check in for the day (uses authenticated employee).

#### POST /api/attendance/check-out
Check out for the day (uses authenticated employee).

#### POST /api/attendance
Create attendance record (admin).

#### PUT /api/attendance/<id>
Update attendance record.

#### DELETE /api/attendance/<id>
Delete attendance record.

### Leaves (`/api/leaves`)

#### GET /api/leaves
Get leave records with filters.
- Query params: `employee_id`, `status`

#### GET /api/leaves/<id>
Get leave by ID.

#### POST /api/leaves
Create leave request.
```json
{
  "leave_type": "vacation",
  "start_date": "2024-03-01",
  "end_date": "2024-03-05",
  "days": 5,
  "reason": "Family vacation"
}
```

#### POST /api/leaves/<id>/approve
Approve leave request.

#### POST /api/leaves/<id>/reject
Reject leave request.

#### PUT /api/leaves/<id>
Update leave request.

#### DELETE /api/leaves/<id>
Delete leave request.

### Payroll (`/api/payroll`)

#### GET /api/payroll
Get payroll records with filters.
- Query params: `employee_id`, `month`, `year`, `status`

#### GET /api/payroll/<id>
Get payroll by ID.

#### POST /api/payroll
Create payroll record.
```json
{
  "employee_id": 1,
  "month": 3,
  "year": 2024,
  "basic_salary": 75000,
  "allowances": 5000,
  "deductions": 2000,
  "bonus": 1000,
  "net_salary": 79000,
  "payment_method": "bank_transfer"
}
```

#### PUT /api/payroll/<id>
Update payroll record.

#### DELETE /api/payroll/<id>
Delete payroll record.

### Recruitment (`/api/recruitment`)

#### GET /api/recruitment/jobs
Get all job postings (public).
- Query params: `status`

#### GET /api/recruitment/jobs/<id>
Get job posting by ID (public).

#### POST /api/recruitment/jobs
Create job posting (requires auth).

#### PUT /api/recruitment/jobs/<id>
Update job posting (requires auth).

#### DELETE /api/recruitment/jobs/<id>
Delete job posting (requires auth).

#### GET /api/recruitment/applicants
Get all applicants (requires auth).
- Query params: `job_id`, `status`

#### GET /api/recruitment/applicants/<id>
Get applicant by ID (requires auth).

#### POST /api/recruitment/apply
Apply for a job (public).
```json
{
  "job_posting_id": 1,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "1234567890",
  "resume_url": "https://...",
  "cover_letter": "...",
  "applied_date": "2024-03-01"
}
```

#### PUT /api/recruitment/applicants/<id>
Update applicant status (requires auth).

#### DELETE /api/recruitment/applicants/<id>
Delete applicant (requires auth).

### Performance (`/api/performance`)

#### GET /api/performance
Get performance reviews with filters.
- Query params: `employee_id`, `status`

#### GET /api/performance/<id>
Get performance review by ID.

#### POST /api/performance
Create performance review.
```json
{
  "employee_id": 1,
  "review_period_start": "2024-01-01",
  "review_period_end": "2024-03-31",
  "rating": 4.5,
  "goals_met": "All quarterly goals achieved",
  "strengths": "Strong technical skills",
  "areas_for_improvement": "Time management",
  "comments": "Excellent performance"
}
```

#### PUT /api/performance/<id>
Update performance review.

#### DELETE /api/performance/<id>
Delete performance review.

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Data Types

### Employee Statuses
- `active`: Currently employed
- `inactive`: Temporarily inactive
- `terminated`: Employment terminated

### Leave Types
- `sick`: Sick leave
- `vacation`: Vacation leave
- `personal`: Personal leave
- `unpaid`: Unpaid leave

### Leave Statuses
- `pending`: Awaiting approval
- `approved`: Approved by manager
- `rejected`: Rejected by manager

### Attendance Statuses
- `present`: Employee present
- `absent`: Employee absent
- `late`: Employee late
- `half-day`: Half day attendance

### Applicant Statuses
- `applied`: Application submitted
- `screening`: Under screening
- `interview`: Interview scheduled
- `offered`: Job offer made
- `rejected`: Application rejected
- `hired`: Hired

### Performance Review Statuses
- `draft`: Review in progress
- `submitted`: Review submitted
- `acknowledged`: Employee acknowledged
