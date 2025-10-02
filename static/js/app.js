// HR Management System Frontend
class HRApp {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5000';
        this.accessToken = localStorage.getItem('accessToken');
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupEnhancedEventListeners();
        if (this.accessToken) {
            this.validateToken();
        } else {
            this.showLogin();
        }
    }

    setupEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Sidebar navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', () => {
                const section = item.dataset.section;
                this.showSection(section);
                this.setActiveMenuItem(item);
            });
        });

        // Add Employee form
        document.getElementById('addEmployeeForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addEmployee();
        });

        // Add Job form
        document.getElementById('addJobForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addJob();
        });
    }

    // Authentication Methods
    async login() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');

        try {
            this.showLoading();
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.accessToken = data.access_token;
                this.currentUser = data.employee;
                localStorage.setItem('accessToken', this.accessToken);
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                this.showDashboard();
                this.loadDashboardData();
            } else {
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            this.hideLoading();
        }
    }

    async validateToken() {
        try {
            const response = await this.apiCall('/api/auth/me');
            if (response.ok) {
                this.currentUser = await response.json();
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                this.showDashboard();
                this.loadDashboardData();
            } else {
                this.logout();
            }
        } catch (error) {
            this.logout();
        }
    }

    logout() {
        this.accessToken = null;
        this.currentUser = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');
        this.showLogin();
    }

    // UI Methods
    showLogin() {
        document.getElementById('loginModal').style.display = 'flex';
        document.getElementById('navbar').style.display = 'none';
        document.getElementById('mainContainer').style.display = 'none';
    }

    showDashboard() {
        document.getElementById('loginModal').style.display = 'none';
        document.getElementById('navbar').style.display = 'flex';
        document.getElementById('mainContainer').style.display = 'flex';
        
        // Update user info
        const userInfo = JSON.parse(localStorage.getItem('currentUser'));
        document.getElementById('currentUser').textContent = 
            `${userInfo.first_name} ${userInfo.last_name} (${userInfo.role})`;
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        document.getElementById(sectionName).classList.add('active');

        // Load section data
        this.loadSectionData(sectionName);
    }

    setActiveMenuItem(activeItem) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        activeItem.classList.add('active');
    }

    showLoading() {
        document.getElementById('loadingSpinner').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loadingSpinner').style.display = 'none';
    }

    // API Helper
    async apiCall(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.accessToken}`,
                ...options.headers,
            },
            ...options,
        };

        return fetch(`${this.baseURL}${endpoint}`, config);
    }

    // Data Loading Methods
    async loadDashboardData() {
        try {
            // Load dashboard statistics
            const employeesResponse = await this.apiCall('/api/employees');
            const leavesResponse = await this.apiCall('/api/leaves');
            const jobsResponse = await this.apiCall('/api/recruitment/jobs');
            const attendanceResponse = await this.apiCall('/api/attendance');

            if (employeesResponse.ok) {
                const employees = await employeesResponse.json();
                document.getElementById('totalEmployees').textContent = employees.length;
            }

            if (leavesResponse.ok) {
                const leaves = await leavesResponse.json();
                const pendingLeaves = leaves.filter(leave => leave.status === 'pending');
                document.getElementById('pendingLeaves').textContent = pendingLeaves.length;
            }

            if (jobsResponse.ok) {
                const jobs = await jobsResponse.json();
                const openJobs = jobs.filter(job => job.status === 'open');
                document.getElementById('openJobs').textContent = openJobs.length;
            }

            if (attendanceResponse.ok) {
                const attendance = await attendanceResponse.json();
                // Calculate present today (this would need more logic for real implementation)
                document.getElementById('presentToday').textContent = attendance.length;
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    // Load departments for dropdowns
    async loadDepartments() {
        try {
            const response = await this.apiCall('/api/employees/departments');
            if (response.ok) {
                const departments = await response.json();
                
                const empDeptSelect = document.getElementById('empDepartment');
                const jobDeptSelect = document.getElementById('jobDepartment');
                
                if (empDeptSelect) {
                    empDeptSelect.innerHTML = '<option value="">Select Department</option>';
                    departments.forEach(dept => {
                        empDeptSelect.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
                    });
                }
                
                if (jobDeptSelect) {
                    jobDeptSelect.innerHTML = '<option value="">Select Department</option>';
                    departments.forEach(dept => {
                        jobDeptSelect.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
                    });
                }
            } else {
                // Fallback to static departments if API fails
                const departments = [
                    { id: 1, name: 'IT' },
                    { id: 2, name: 'HR' },
                    { id: 3, name: 'Finance' },
                    { id: 4, name: 'Sales' },
                    { id: 5, name: 'Marketing' }
                ];
                
                const empDeptSelect = document.getElementById('empDepartment');
                const jobDeptSelect = document.getElementById('jobDepartment');
                
                if (empDeptSelect) {
                    empDeptSelect.innerHTML = '<option value="">Select Department</option>';
                    departments.forEach(dept => {
                        empDeptSelect.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
                    });
                }
                
                if (jobDeptSelect) {
                    jobDeptSelect.innerHTML = '<option value="">Select Department</option>';
                    departments.forEach(dept => {
                        jobDeptSelect.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
                    });
                }
            }
        } catch (error) {
            console.error('Error loading departments:', error);
        }
    }

    // Employee Management
    async addEmployee() {
        const form = document.getElementById('addEmployeeForm');
        const formData = new FormData(form);
        const errorDiv = document.getElementById('addEmployeeError');
        
        const employeeData = {
            employee_id: formData.get('employee_id'),
            email: formData.get('email'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            position: formData.get('position'),
            department_id: formData.get('department_id') ? parseInt(formData.get('department_id')) : null,
            salary: formData.get('salary') ? parseFloat(formData.get('salary')) : null,
            hire_date: formData.get('hire_date'),
            phone: formData.get('phone'),
            role: formData.get('role'),
            password: formData.get('password')
        };

        try {
            this.showLoading();
            const response = await this.apiCall('/api/employees', {
                method: 'POST',
                body: JSON.stringify(employeeData)
            });

            if (response.ok) {
                errorDiv.innerHTML = '✅ Employee added successfully!';
                errorDiv.className = 'success-message';
                errorDiv.style.display = 'block';
                form.reset();
                setTimeout(() => {
                    this.hideAddEmployeeModal();
                    this.loadEmployees(); // Refresh the employee list
                }, 2000);
            } else {
                const errorData = await response.json();
                errorDiv.innerHTML = `❌ Error: ${errorData.error || 'Failed to add employee'}`;
                errorDiv.className = 'error-message';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.innerHTML = '❌ Network error. Please try again.';
            errorDiv.className = 'error-message';
            errorDiv.style.display = 'block';
        } finally {
            this.hideLoading();
        }
    }

    // Job Management
    async addJob() {
        const form = document.getElementById('addJobForm');
        const formData = new FormData(form);
        const errorDiv = document.getElementById('addJobError');
        
        const jobData = {
            title: formData.get('title'),
            description: formData.get('description'),
            department_id: formData.get('department_id') ? parseInt(formData.get('department_id')) : null,
            requirements: formData.get('requirements'),
            salary_range: formData.get('salary_range'),
            location: formData.get('location'),
            employment_type: formData.get('employment_type'),
            posted_date: formData.get('posted_date'),
            closing_date: formData.get('closing_date') || null,
            posted_by: this.currentUser.id
        };

        try {
            this.showLoading();
            const response = await this.apiCall('/api/recruitment/jobs', {
                method: 'POST',
                body: JSON.stringify(jobData)
            });

            if (response.ok) {
                errorDiv.innerHTML = '✅ Job posted successfully!';
                errorDiv.className = 'success-message';
                errorDiv.style.display = 'block';
                form.reset();
                setTimeout(() => {
                    this.hideAddJobModal();
                    this.loadRecruitment(); // Refresh the jobs list
                }, 2000);
            } else {
                const errorData = await response.json();
                errorDiv.innerHTML = `❌ Error: ${errorData.error || 'Failed to post job'}`;
                errorDiv.className = 'error-message';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.innerHTML = '❌ Network error. Please try again.';
            errorDiv.className = 'error-message';
            errorDiv.style.display = 'block';
        } finally {
            this.hideLoading();
        }
    }

    // Leave Management
    async approveLeave(leaveId) {
        try {
            this.showLoading();
            const response = await this.apiCall(`/api/leaves/${leaveId}/approve`, {
                method: 'POST'
            });

            if (response.ok) {
                this.loadLeaves(); // Refresh the leaves list
            } else {
                console.error('Failed to approve leave');
            }
        } catch (error) {
            console.error('Error approving leave:', error);
        } finally {
            this.hideLoading();
        }
    }

    async rejectLeave(leaveId) {
        try {
            this.showLoading();
            const response = await this.apiCall(`/api/leaves/${leaveId}/reject`, {
                method: 'POST'
            });

            if (response.ok) {
                this.loadLeaves(); // Refresh the leaves list
            } else {
                console.error('Failed to reject leave');
            }
        } catch (error) {
            console.error('Error rejecting leave:', error);
        } finally {
            this.hideLoading();
        }
    }

    // View Employee Details
    async viewEmployee(employeeId) {
        try {
            this.showLoading();
            const response = await this.apiCall(`/api/employees/${employeeId}`);
            
            if (response.ok) {
                const employee = await response.json();
                this.showEmployeeDetails(employee);
            } else {
                console.error('Failed to load employee details');
            }
        } catch (error) {
            console.error('Error loading employee details:', error);
        } finally {
            this.hideLoading();
        }
    }

    showEmployeeDetails(employee) {
        const modal = document.getElementById('viewEmployeeModal');
        const detailsDiv = document.getElementById('employeeDetails');
        
        detailsDiv.innerHTML = `
            <div class="detail-item">
                <div class="detail-label">Employee ID</div>
                <div class="detail-value">${employee.employee_id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Name</div>
                <div class="detail-value">${employee.first_name} ${employee.last_name}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Email</div>
                <div class="detail-value">${employee.email}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Phone</div>
                <div class="detail-value">${employee.phone || 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Position</div>
                <div class="detail-value">${employee.position}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Role</div>
                <div class="detail-value">${employee.role}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Hire Date</div>
                <div class="detail-value">${employee.hire_date}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Salary</div>
                <div class="detail-value">$${employee.salary ? employee.salary.toLocaleString() : 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Status</div>
                <div class="detail-value">
                    <span class="status-badge status-${employee.status}">${employee.status}</span>
                </div>
            </div>
            <div class="detail-item full-width">
                <div class="detail-label">Address</div>
                <div class="detail-value">${employee.address || 'N/A'}</div>
            </div>
        `;
        
        modal.style.display = 'flex';
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'employees':
                await this.loadEmployees();
                break;
            case 'attendance':
                await this.loadAttendance();
                break;
            case 'leaves':
                await this.loadLeaves();
                break;
            case 'payroll':
                await this.loadPayroll();
                break;
            case 'recruitment':
                await this.loadRecruitment();
                break;
            case 'performance':
                await this.loadPerformance();
                break;
        }
    }

    async loadEmployees() {
        try {
            const response = await this.apiCall('/api/employees');
            if (response.ok) {
                const employees = await response.json();
                this.renderEmployeesTable(employees);
            } else {
                console.error('Failed to load employees');
            }
        } catch (error) {
            console.error('Error loading employees:', error);
        }
    }

    async loadAttendance() {
        try {
            const response = await this.apiCall('/api/attendance');
            if (response.ok) {
                const attendance = await response.json();
                this.renderAttendanceTable(attendance);
            }
        } catch (error) {
            console.error('Error loading attendance:', error);
        }
    }

    async loadLeaves() {
        try {
            const response = await this.apiCall('/api/leaves');
            if (response.ok) {
                const leaves = await response.json();
                this.renderLeavesTable(leaves);
            }
        } catch (error) {
            console.error('Error loading leaves:', error);
        }
    }

    async loadPayroll() {
        try {
            const response = await this.apiCall('/api/payroll');
            if (response.ok) {
                const payroll = await response.json();
                this.renderPayrollTable(payroll);
            }
        } catch (error) {
            console.error('Error loading payroll:', error);
        }
    }

    async loadRecruitment() {
        try {
            const response = await this.apiCall('/api/recruitment/jobs');
            if (response.ok) {
                const jobs = await response.json();
                this.renderJobsTable(jobs);
            }
            
            const applicantsResponse = await this.apiCall('/api/recruitment/applicants');
            if (applicantsResponse.ok) {
                const applicants = await applicantsResponse.json();
                this.renderApplicantsTable(applicants);
            }
        } catch (error) {
            console.error('Error loading recruitment data:', error);
        }
    }

    async loadPerformance() {
        try {
            const response = await this.apiCall('/api/performance');
            if (response.ok) {
                const reviews = await response.json();
                this.renderPerformanceTable(reviews);
            }
        } catch (error) {
            console.error('Error loading performance data:', error);
        }
    }

    // Render Methods
    renderEmployeesTable(employees) {
        const tbody = document.getElementById('employeesTableBody');
        tbody.innerHTML = '';

        employees.forEach(employee => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${employee.employee_id}</td>
                <td>${employee.first_name} ${employee.last_name}</td>
                <td>${employee.email}</td>
                <td>${employee.position || 'N/A'}</td>
                <td>${employee.department_name || 'N/A'}</td>
                <td><span class="status-badge status-${employee.status}">${employee.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="window.hrApp.viewEmployee(${employee.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-secondary" onclick="editEmployee(${employee.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderAttendanceTable(attendance) {
        const tbody = document.getElementById('attendanceTableBody');
        tbody.innerHTML = '';

        attendance.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.employee_name || 'N/A'}</td>
                <td>${record.date}</td>
                <td>${record.check_in || '-'}</td>
                <td>${record.check_out || '-'}</td>
                <td><span class="status-badge status-${record.status}">${record.status}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    renderLeavesTable(leaves) {
        const tbody = document.getElementById('leavesTableBody');
        tbody.innerHTML = '';

        leaves.forEach(leave => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${leave.employee_name || 'N/A'}</td>
                <td>${leave.leave_type}</td>
                <td>${leave.start_date}</td>
                <td>${leave.end_date}</td>
                <td>${leave.days}</td>
                <td><span class="status-badge status-${leave.status}">${leave.status}</span></td>
                <td>
                    ${leave.status === 'pending' ? `
                        <div class="leave-actions">
                            <button class="action-btn btn-success" onclick="window.hrApp.approveLeave(${leave.id})">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="action-btn btn-danger" onclick="window.hrApp.rejectLeave(${leave.id})">
                                <i class="fas fa-times"></i> Reject
                            </button>
                        </div>
                    ` : '-'}
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderPayrollTable(payroll) {
        const tbody = document.getElementById('payrollTableBody');
        tbody.innerHTML = '';

        payroll.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.employee_name || 'N/A'}</td>
                <td>${record.month}/${record.year}</td>
                <td>$${record.basic_salary.toLocaleString()}</td>
                <td>$${record.allowances.toLocaleString()}</td>
                <td>$${record.deductions.toLocaleString()}</td>
                <td>$${record.net_salary.toLocaleString()}</td>
                <td><span class="status-badge status-${record.status}">${record.status}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    renderJobsTable(jobs) {
        const tbody = document.getElementById('jobsTableBody');
        tbody.innerHTML = '';

        jobs.forEach(job => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${job.title}</td>
                <td>${job.department_name || 'N/A'}</td>
                <td>${job.posted_date}</td>
                <td><span class="status-badge status-${job.status}">${job.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewJob(${job.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-secondary" onclick="editJob(${job.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderApplicantsTable(applicants) {
        const tbody = document.getElementById('applicantsTableBody');
        tbody.innerHTML = '';

        applicants.forEach(applicant => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${applicant.first_name} ${applicant.last_name}</td>
                <td>${applicant.email}</td>
                <td>${applicant.job_title || 'N/A'}</td>
                <td>${applicant.applied_date}</td>
                <td><span class="status-badge status-${applicant.status}">${applicant.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewApplicant(${applicant.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-success" onclick="updateApplicantStatus(${applicant.id}, 'interview')">
                        <i class="fas fa-user-check"></i> Interview
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderPerformanceTable(reviews) {
        const tbody = document.getElementById('performanceTableBody');
        tbody.innerHTML = '';

        reviews.forEach(review => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${review.employee_name || 'N/A'}</td>
                <td>${review.reviewer_name || 'N/A'}</td>
                <td>${review.review_period_start} - ${review.review_period_end}</td>
                <td>${review.rating}/5</td>
                <td><span class="status-badge status-${review.status}">${review.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewReview(${review.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // NEW FEATURE METHODS

    // Training Program Management
    async loadTrainingPrograms() {
        try {
            const response = await fetch(`${this.baseURL}/api/training/programs`, {
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const programs = await response.json();
                this.renderTrainingTable(programs);
            }
        } catch (error) {
            console.error('Error loading training programs:', error);
        }
    }

    async addTrainingProgram() {
        const form = document.getElementById('addTrainingForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch(`${this.baseURL}/api/training/programs`, {
                method: 'POST',
                headers: {
                    ...this.getHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                hideAddTrainingModal();
                this.loadTrainingPrograms();
                this.showMessage('Training program added successfully!', 'success');
            } else {
                const error = await response.json();
                document.getElementById('addTrainingError').textContent = error.error;
                document.getElementById('addTrainingError').style.display = 'block';
            }
        } catch (error) {
            console.error('Error adding training program:', error);
        }
    }

    async loadTrainingEnrollments() {
        try {
            const response = await fetch(`${this.baseURL}/api/training/enrollments`, {
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const enrollments = await response.json();
                this.renderEnrollmentsTable(enrollments);
            }
        } catch (error) {
            console.error('Error loading training enrollments:', error);
        }
    }

    // Benefits Management
    async loadBenefits() {
        try {
            const response = await fetch(`${this.baseURL}/api/training/benefits`, {
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const benefits = await response.json();
                this.renderBenefitsTable(benefits);
            }
        } catch (error) {
            console.error('Error loading benefits:', error);
        }
    }

    async addBenefit() {
        const form = document.getElementById('addBenefitForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch(`${this.baseURL}/api/training/benefits`, {
                method: 'POST',
                headers: {
                    ...this.getHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                hideAddBenefitModal();
                this.loadBenefits();
                this.showMessage('Benefit added successfully!', 'success');
            } else {
                const error = await response.json();
                document.getElementById('addBenefitError').textContent = error.error;
                document.getElementById('addBenefitError').style.display = 'block';
            }
        } catch (error) {
            console.error('Error adding benefit:', error);
        }
    }

    // Document Management
    async loadDocuments() {
        try {
            const response = await fetch(`${this.baseURL}/api/training/documents`, {
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const documents = await response.json();
                this.renderDocumentsTable(documents);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    async addDocument() {
        const form = document.getElementById('addDocumentForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch(`${this.baseURL}/api/training/documents`, {
                method: 'POST',
                headers: {
                    ...this.getHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                hideAddDocumentModal();
                this.loadDocuments();
                this.showMessage('Document uploaded successfully!', 'success');
            } else {
                const error = await response.json();
                document.getElementById('addDocumentError').textContent = error.error;
                document.getElementById('addDocumentError').style.display = 'block';
            }
        } catch (error) {
            console.error('Error uploading document:', error);
        }
    }

    // Utility Methods
    async loadEmployeeOptionsForSelect(selectId) {
        try {
            const response = await fetch(`${this.baseURL}/api/employees`, {
                headers: this.getHeaders()
            });
            
            if (response.ok) {
                const employees = await response.json();
                const select = document.getElementById(selectId);
                select.innerHTML = '<option value="">Select Employee</option>';
                
                employees.forEach(employee => {
                    const option = document.createElement('option');
                    option.value = employee.id;
                    option.textContent = `${employee.first_name} ${employee.last_name}`;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading employees for select:', error);
        }
    }

    // Render Methods for New Features
    renderTrainingTable(programs) {
        const tbody = document.getElementById('trainingTableBody');
        tbody.innerHTML = '';

        programs.forEach(program => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${program.title}</td>
                <td>${program.trainer || 'N/A'}</td>
                <td>${program.start_date}</td>
                <td>${program.duration_hours || 'N/A'} hours</td>
                <td>${program.current_participants}/${program.max_participants}</td>
                <td><span class="status-badge status-${program.status}">${program.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewTraining(${program.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-warning" onclick="editTraining(${program.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderEnrollmentsTable(enrollments) {
        const tbody = document.getElementById('enrollmentsTableBody');
        tbody.innerHTML = '';

        enrollments.forEach(enrollment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${enrollment.employee_name || 'N/A'}</td>
                <td>${enrollment.program_title || 'N/A'}</td>
                <td>${enrollment.enrollment_date}</td>
                <td><span class="status-badge status-${enrollment.completion_status}">${enrollment.completion_status}</span></td>
                <td>${enrollment.score || 'N/A'}</td>
                <td>
                    <button class="action-btn btn-success" onclick="completeTraining(${enrollment.id})">
                        <i class="fas fa-check"></i> Complete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderBenefitsTable(benefits) {
        const tbody = document.getElementById('benefitsTableBody');
        tbody.innerHTML = '';

        benefits.forEach(benefit => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${benefit.employee_name || 'N/A'}</td>
                <td>${benefit.benefit_type}</td>
                <td>${benefit.benefit_name}</td>
                <td>${benefit.provider || 'N/A'}</td>
                <td>$${benefit.premium_amount || '0'}</td>
                <td><span class="status-badge status-${benefit.status}">${benefit.status}</span></td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewBenefit(${benefit.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-warning" onclick="editBenefit(${benefit.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderDocumentsTable(documents) {
        const tbody = document.getElementById('documentsTableBody');
        tbody.innerHTML = '';

        documents.forEach(document => {
            const row = document.createElement('tr');
            const fileSize = document.file_size ? (document.file_size / 1024).toFixed(1) + ' KB' : 'N/A';
            
            row.innerHTML = `
                <td>${document.document_name}</td>
                <td>${document.employee_name || 'N/A'}</td>
                <td>${document.document_type}</td>
                <td>${document.uploaded_at}</td>
                <td>${fileSize}</td>
                <td>
                    <button class="action-btn btn-primary" onclick="viewDocument(${document.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn btn-danger" onclick="deleteDocument(${document.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Report Generation
    async generateReport(type) {
        try {
            this.showLoading();
            
            // Simulate report generation
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            this.hideLoading();
            this.showMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} report generated successfully!`, 'success');
            
            // In a real implementation, this would download or display the report
            console.log(`Generated ${type} report`);
        } catch (error) {
            this.hideLoading();
            console.error(`Error generating ${type} report:`, error);
        }
    }

    // Update section loading to include new features
    async loadSectionData(section) {
        switch(section) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'employees':
                await this.loadEmployees();
                break;
            case 'attendance':
                await this.loadAttendance();
                break;
            case 'leaves':
                await this.loadLeaves();
                break;
            case 'payroll':
                await this.loadPayroll();
                break;
            case 'recruitment':
                await this.loadRecruitment();
                break;
            case 'performance':
                await this.loadPerformance();
                break;
            case 'training':
                await this.loadTrainingPrograms();
                break;
            case 'benefits':
                await this.loadBenefits();
                break;
            case 'documents':
                await this.loadDocuments();
                break;
            case 'reports':
                // Reports section doesn't need to load data
                break;
            default:
                console.log('Unknown section:', section);
        }
    }

    // Enhanced show section method
    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(s => {
            s.classList.remove('active');
        });

        // Show selected section
        const sectionElement = document.getElementById(section);
        if (sectionElement) {
            sectionElement.classList.add('active');
            this.loadSectionData(section);
        }
    }

    // Enhanced form event listeners
    setupEnhancedEventListeners() {
        // Training form
        const trainingForm = document.getElementById('addTrainingForm');
        if (trainingForm) {
            trainingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addTrainingProgram();
            });
        }

        // Benefits form
        const benefitForm = document.getElementById('addBenefitForm');
        if (benefitForm) {
            benefitForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addBenefit();
            });
        }

        // Document form
        const documentForm = document.getElementById('addDocumentForm');
        if (documentForm) {
            documentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addDocument();
            });
        }
    }
}

// Global Functions for Button Actions
function showJobPostings() {
    document.querySelector('.tab-btn.active').classList.remove('active');
    document.querySelector('.tab-btn').classList.add('active');
    document.getElementById('jobPostings').style.display = 'block';
    document.getElementById('applicants').style.display = 'none';
}

function showApplicants() {
    document.querySelector('.tab-btn.active').classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    document.getElementById('jobPostings').style.display = 'none';
    document.getElementById('applicants').style.display = 'block';
}

// Modal Management Functions
function showAddEmployeeModal() {
    window.hrApp.loadDepartments();
    document.getElementById('addEmployeeModal').style.display = 'flex';
    // Set default date to today
    document.getElementById('empHireDate').value = new Date().toISOString().split('T')[0];
}

function hideAddEmployeeModal() {
    document.getElementById('addEmployeeModal').style.display = 'none';
    document.getElementById('addEmployeeForm').reset();
    document.getElementById('addEmployeeError').style.display = 'none';
}

function showAddJobModal() {
    window.hrApp.loadDepartments();
    document.getElementById('addJobModal').style.display = 'flex';
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('jobPostedDate').value = today;
}

function hideAddJobModal() {
    document.getElementById('addJobModal').style.display = 'none';
    document.getElementById('addJobForm').reset();
    document.getElementById('addJobError').style.display = 'none';
}

function hideViewEmployeeModal() {
    document.getElementById('viewEmployeeModal').style.display = 'none';
}

// Employee Management Functions
async function editEmployee(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/employees/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const employee = await response.json();
            
            // Populate edit form with employee data
            document.getElementById('empFirstName').value = employee.first_name;
            document.getElementById('empLastName').value = employee.last_name;
            document.getElementById('empEmail').value = employee.email;
            document.getElementById('empPhone').value = employee.phone || '';
            document.getElementById('empDepartment').value = employee.department_id || '';
            document.getElementById('empPosition').value = employee.position || '';
            document.getElementById('empSalary').value = employee.salary || '';
            document.getElementById('empHireDate').value = employee.hire_date || '';
            document.getElementById('empStatus').value = employee.status || 'active';
            
            // Change form submit to update instead of create
            const form = document.getElementById('addEmployeeForm');
            form.onsubmit = async (e) => {
                e.preventDefault();
                await updateEmployee(id);
            };
            
            document.getElementById('addEmployeeModal').style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading employee:', error);
        alert('Failed to load employee data');
    }
}

async function updateEmployee(id) {
    const form = document.getElementById('addEmployeeForm');
    const formData = new FormData(form);
    const errorDiv = document.getElementById('addEmployeeError');
    
    const employeeData = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        department_id: formData.get('department_id') ? parseInt(formData.get('department_id')) : null,
        position: formData.get('position'),
        salary: formData.get('salary') ? parseFloat(formData.get('salary')) : null,
        hire_date: formData.get('hire_date'),
        status: formData.get('status')
    };

    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/employees/${id}`, {
            method: 'PUT',
            headers: {
                ...window.hrApp.getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(employeeData)
        });

        if (response.ok) {
            errorDiv.innerHTML = '✅ Employee updated successfully!';
            errorDiv.className = 'success-message';
            errorDiv.style.display = 'block';
            setTimeout(() => {
                hideAddEmployeeModal();
                window.hrApp.loadEmployees();
                // Reset form handler
                form.onsubmit = (e) => {
                    e.preventDefault();
                    window.hrApp.addEmployee();
                };
            }, 1500);
        } else {
            const error = await response.json();
            errorDiv.innerHTML = `❌ Error: ${error.error}`;
            errorDiv.className = 'error-message';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.innerHTML = '❌ Network error. Please try again.';
        errorDiv.className = 'error-message';
        errorDiv.style.display = 'block';
    }
}

// Job Management Functions
async function viewJob(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/recruitment/jobs/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const job = await response.json();
            
            // Create and show modal with job details
            const modalHtml = `
                <div class="modal" id="viewJobModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Job Details</h2>
                            <span class="close" onclick="document.getElementById('viewJobModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${job.title}</h3>
                            <p><strong>Department:</strong> ${job.department || 'N/A'}</p>
                            <p><strong>Location:</strong> ${job.location || 'N/A'}</p>
                            <p><strong>Employment Type:</strong> ${job.employment_type || 'N/A'}</p>
                            <p><strong>Salary Range:</strong> ${job.salary_range || 'N/A'}</p>
                            <p><strong>Posted Date:</strong> ${job.posted_date || 'N/A'}</p>
                            <p><strong>Closing Date:</strong> ${job.closing_date || 'Open'}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${job.status}">${job.status}</span></p>
                            <div class="mt-3">
                                <h4>Description</h4>
                                <p>${job.description || 'No description available'}</p>
                            </div>
                            <div class="mt-3">
                                <h4>Requirements</h4>
                                <p>${job.requirements || 'No requirements specified'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewJobModal').remove()">Close</button>
                            <button class="btn-primary" onclick="editJob(${id}); document.getElementById('viewJobModal').remove()">Edit Job</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading job:', error);
        alert('Failed to load job details');
    }
}

async function editJob(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/recruitment/jobs/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const job = await response.json();
            
            // Populate job form with data
            document.getElementById('jobTitle').value = job.title;
            document.getElementById('jobDescription').value = job.description || '';
            document.getElementById('jobDepartment').value = job.department_id || '';
            document.getElementById('jobRequirements').value = job.requirements || '';
            document.getElementById('jobSalaryRange').value = job.salary_range || '';
            document.getElementById('jobLocation').value = job.location || '';
            document.getElementById('jobEmploymentType').value = job.employment_type || '';
            document.getElementById('jobPostedDate').value = job.posted_date || '';
            document.getElementById('jobClosingDate').value = job.closing_date || '';
            
            // Change form submit to update
            const form = document.getElementById('addJobForm');
            form.onsubmit = async (e) => {
                e.preventDefault();
                await updateJob(id);
            };
            
            document.getElementById('addJobModal').style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading job:', error);
        alert('Failed to load job data');
    }
}

async function updateJob(id) {
    const form = document.getElementById('addJobForm');
    const formData = new FormData(form);
    const errorDiv = document.getElementById('addJobError');
    
    const jobData = {
        title: formData.get('title'),
        description: formData.get('description'),
        department_id: formData.get('department_id') ? parseInt(formData.get('department_id')) : null,
        requirements: formData.get('requirements'),
        salary_range: formData.get('salary_range'),
        location: formData.get('location'),
        employment_type: formData.get('employment_type'),
        posted_date: formData.get('posted_date'),
        closing_date: formData.get('closing_date') || null
    };

    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/recruitment/jobs/${id}`, {
            method: 'PUT',
            headers: {
                ...window.hrApp.getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });

        if (response.ok) {
            errorDiv.innerHTML = '✅ Job updated successfully!';
            errorDiv.className = 'success-message';
            errorDiv.style.display = 'block';
            setTimeout(() => {
                hideAddJobModal();
                window.hrApp.loadRecruitment();
                // Reset form handler
                form.onsubmit = (e) => {
                    e.preventDefault();
                    window.hrApp.addJob();
                };
            }, 1500);
        } else {
            const error = await response.json();
            errorDiv.innerHTML = `❌ Error: ${error.error}`;
            errorDiv.className = 'error-message';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.innerHTML = '❌ Network error. Please try again.';
        errorDiv.className = 'error-message';
        errorDiv.style.display = 'block';
    }
}

// Applicant Management Functions
async function viewApplicant(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/recruitment/applicants/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const applicant = await response.json();
            
            // Create and show modal with applicant details
            const modalHtml = `
                <div class="modal" id="viewApplicantModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Applicant Details</h2>
                            <span class="close" onclick="document.getElementById('viewApplicantModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${applicant.name}</h3>
                            <p><strong>Email:</strong> ${applicant.email}</p>
                            <p><strong>Phone:</strong> ${applicant.phone || 'N/A'}</p>
                            <p><strong>Job Applied:</strong> ${applicant.job_title || 'N/A'}</p>
                            <p><strong>Application Date:</strong> ${applicant.application_date || 'N/A'}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${applicant.status}">${applicant.status}</span></p>
                            <div class="mt-3">
                                <h4>Cover Letter</h4>
                                <p>${applicant.cover_letter || 'No cover letter provided'}</p>
                            </div>
                            <div class="mt-3">
                                <h4>Resume</h4>
                                <p>${applicant.resume_path ? '<a href="' + applicant.resume_path + '" target="_blank">View Resume</a>' : 'No resume uploaded'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewApplicantModal').remove()">Close</button>
                            <button class="btn-success" onclick="updateApplicantStatus(${id}, 'screening'); document.getElementById('viewApplicantModal').remove()">Move to Screening</button>
                            <button class="btn-warning" onclick="updateApplicantStatus(${id}, 'interview'); document.getElementById('viewApplicantModal').remove()">Schedule Interview</button>
                            <button class="btn-danger" onclick="updateApplicantStatus(${id}, 'rejected'); document.getElementById('viewApplicantModal').remove()">Reject</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading applicant:', error);
        alert('Failed to load applicant details');
    }
}

async function updateApplicantStatus(id, status) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/recruitment/applicants/${id}/status`, {
            method: 'PUT',
            headers: {
                ...window.hrApp.getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });

        if (response.ok) {
            window.hrApp.showMessage(`Applicant status updated to ${status}`, 'success');
            window.hrApp.loadRecruitment();
        } else {
            const error = await response.json();
            alert(`Failed to update status: ${error.error}`);
        }
    } catch (error) {
        console.error('Error updating applicant status:', error);
        alert('Failed to update applicant status');
    }
}

// NEW FEATURES FUNCTIONS

// Training Management
function showAddTrainingModal() {
    document.getElementById('addTrainingModal').style.display = 'block';
    document.getElementById('trainingStartDate').value = new Date().toISOString().split('T')[0];
}

function hideAddTrainingModal() {
    document.getElementById('addTrainingModal').style.display = 'none';
    document.getElementById('addTrainingForm').reset();
    document.getElementById('addTrainingError').style.display = 'none';
}

function showTrainingPrograms(event) {
    document.getElementById('trainingPrograms').style.display = 'block';
    document.getElementById('trainingEnrollments').style.display = 'none';
    
    // Update tab buttons
    document.querySelectorAll('.training-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    app.loadTrainingPrograms();
}

function showTrainingEnrollments(event) {
    document.getElementById('trainingPrograms').style.display = 'none';
    document.getElementById('trainingEnrollments').style.display = 'block';
    
    // Update tab buttons
    document.querySelectorAll('.training-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    app.loadTrainingEnrollments();
}

// Benefits Management
function showAddBenefitModal() {
    document.getElementById('addBenefitModal').style.display = 'block';
    app.loadEmployeeOptionsForSelect('benefitEmployee');
    document.getElementById('benefitStartDate').value = new Date().toISOString().split('T')[0];
}

function hideAddBenefitModal() {
    document.getElementById('addBenefitModal').style.display = 'none';
    document.getElementById('addBenefitForm').reset();
    document.getElementById('addBenefitError').style.display = 'none';
}

// Document Management
function showAddDocumentModal() {
    document.getElementById('addDocumentModal').style.display = 'block';
    app.loadEmployeeOptionsForSelect('docEmployee');
}

function hideAddDocumentModal() {
    document.getElementById('addDocumentModal').style.display = 'none';
    document.getElementById('addDocumentForm').reset();
    document.getElementById('addDocumentError').style.display = 'none';
}

// Reports Functions
async function exportReports() {
    const exportOptions = ['CSV', 'PDF', 'Excel'];
    const reportTypes = ['employees', 'attendance', 'leaves', 'payroll', 'performance', 'training'];
    
    // Create export dialog
    const modalHtml = `
        <div class="modal" id="exportModal" style="display: flex;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Export Reports</h2>
                    <span class="close" onclick="document.getElementById('exportModal').remove()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Report Type:</label>
                        <select id="exportReportType" class="form-control">
                            <option value="employees">Employees</option>
                            <option value="attendance">Attendance</option>
                            <option value="leaves">Leaves</option>
                            <option value="payroll">Payroll</option>
                            <option value="performance">Performance</option>
                            <option value="training">Training</option>
                            <option value="all">All Reports</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Export Format:</label>
                        <select id="exportFormat" class="form-control">
                            <option value="csv">CSV</option>
                            <option value="json">JSON</option>
                            <option value="pdf">PDF</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Date Range:</label>
                        <input type="date" id="exportStartDate" class="form-control" />
                        <label>to</label>
                        <input type="date" id="exportEndDate" class="form-control" />
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="document.getElementById('exportModal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="processExport()">Export</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

async function processExport() {
    const reportType = document.getElementById('exportReportType').value;
    const format = document.getElementById('exportFormat').value;
    const startDate = document.getElementById('exportStartDate').value;
    const endDate = document.getElementById('exportEndDate').value;
    
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/analytics/export`, {
            method: 'POST',
            headers: {
                ...window.hrApp.getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: reportType,
                format: format,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${reportType}_report_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            document.getElementById('exportModal').remove();
            window.hrApp.showMessage('Report exported successfully!', 'success');
        } else {
            alert('Failed to export report. Using mock data download.');
            // Fallback to mock CSV export
            downloadMockCSV(reportType);
            document.getElementById('exportModal').remove();
        }
    } catch (error) {
        console.error('Export error:', error);
        // Fallback to mock CSV export
        downloadMockCSV(reportType);
        document.getElementById('exportModal').remove();
    }
}

function downloadMockCSV(reportType) {
    let csvContent = '';
    const timestamp = new Date().toISOString().split('T')[0];
    
    switch(reportType) {
        case 'employees':
            csvContent = 'ID,Name,Email,Department,Position,Status\n';
            csvContent += '1,John Doe,john@example.com,Engineering,Developer,Active\n';
            break;
        case 'attendance':
            csvContent = 'Date,Employee,Check In,Check Out,Status\n';
            csvContent += `${timestamp},John Doe,09:00,17:00,Present\n`;
            break;
        case 'leaves':
            csvContent = 'Employee,Leave Type,Start Date,End Date,Status\n';
            csvContent += 'John Doe,Vacation,2025-01-01,2025-01-05,Approved\n';
            break;
        default:
            csvContent = 'Report Type,Generated Date\n';
            csvContent += `${reportType},${timestamp}\n`;
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportType}_report_${timestamp}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    window.hrApp.showMessage('Report exported successfully!', 'success');
}

function generateEmployeeReport() {
    window.hrApp.generateReport('employees');
}

function generateAttendanceReport() {
    window.hrApp.generateReport('attendance');
}

function generateLeaveReport() {
    window.hrApp.generateReport('leaves');
}

function generatePayrollReport() {
    window.hrApp.generateReport('payroll');
}

function generatePerformanceReport() {
    window.hrApp.generateReport('performance');
}

function generateTrainingReport() {
    window.hrApp.generateReport('training');
}

async function viewReview(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/performance/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const review = await response.json();
            
            // Create and show modal with review details
            const modalHtml = `
                <div class="modal" id="viewReviewModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Performance Review Details</h2>
                            <span class="close" onclick="document.getElementById('viewReviewModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${review.employee_name || 'Employee'}</h3>
                            <p><strong>Review Period:</strong> ${review.review_period || 'N/A'}</p>
                            <p><strong>Review Date:</strong> ${review.review_date || 'N/A'}</p>
                            <p><strong>Reviewer:</strong> ${review.reviewer || 'N/A'}</p>
                            <p><strong>Overall Rating:</strong> <span class="badge">${review.rating || 0}/5</span></p>
                            <div class="mt-3">
                                <h4>Goals</h4>
                                <p>${review.goals || 'No goals specified'}</p>
                            </div>
                            <div class="mt-3">
                                <h4>Achievements</h4>
                                <p>${review.achievements || 'No achievements recorded'}</p>
                            </div>
                            <div class="mt-3">
                                <h4>Areas for Improvement</h4>
                                <p>${review.improvements || 'No improvement areas noted'}</p>
                            </div>
                            <div class="mt-3">
                                <h4>Comments</h4>
                                <p>${review.comments || 'No additional comments'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewReviewModal').remove()">Close</button>
                            <button class="btn-primary" onclick="editReview(${id}); document.getElementById('viewReviewModal').remove()">Edit Review</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading review:', error);
        alert('Failed to load review details');
    }
}

async function editReview(id) {
    alert('Edit review feature - Redirect to performance review edit page');
    // This would typically open an edit form or redirect to edit page
}

// Training Management Functions
async function viewTraining(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/training/programs/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const program = await response.json();
            
            const modalHtml = `
                <div class="modal" id="viewTrainingModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Training Program Details</h2>
                            <span class="close" onclick="document.getElementById('viewTrainingModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${program.title}</h3>
                            <p><strong>Trainer:</strong> ${program.trainer || 'N/A'}</p>
                            <p><strong>Start Date:</strong> ${program.start_date}</p>
                            <p><strong>End Date:</strong> ${program.end_date || 'N/A'}</p>
                            <p><strong>Duration:</strong> ${program.duration_hours || 'N/A'} hours</p>
                            <p><strong>Location:</strong> ${program.location || 'N/A'}</p>
                            <p><strong>Max Participants:</strong> ${program.max_participants}</p>
                            <p><strong>Current Participants:</strong> ${program.current_participants}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${program.status}">${program.status}</span></p>
                            <div class="mt-3">
                                <h4>Description</h4>
                                <p>${program.description || 'No description available'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewTrainingModal').remove()">Close</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading training:', error);
        alert('Failed to load training details');
    }
}

async function editTraining(id) {
    alert('Edit training feature - Would open edit modal with training details');
    // This would typically open an edit form similar to add training
}

async function viewBenefit(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/training/benefits/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const benefit = await response.json();
            
            const modalHtml = `
                <div class="modal" id="viewBenefitModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Benefit Details</h2>
                            <span class="close" onclick="document.getElementById('viewBenefitModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${benefit.benefit_type}</h3>
                            <p><strong>Employee:</strong> ${benefit.employee_name || 'N/A'}</p>
                            <p><strong>Provider:</strong> ${benefit.provider || 'N/A'}</p>
                            <p><strong>Start Date:</strong> ${benefit.start_date}</p>
                            <p><strong>End Date:</strong> ${benefit.end_date || 'N/A'}</p>
                            <p><strong>Coverage Amount:</strong> ${benefit.coverage_amount || 'N/A'}</p>
                            <p><strong>Employee Contribution:</strong> ${benefit.employee_contribution || 'N/A'}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${benefit.status}">${benefit.status}</span></p>
                            <div class="mt-3">
                                <h4>Description</h4>
                                <p>${benefit.description || 'No description available'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewBenefitModal').remove()">Close</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading benefit:', error);
        alert('Failed to load benefit details');
    }
}

async function editBenefit(id) {
    alert('Edit benefit feature - Would open edit modal with benefit details');
    // This would typically open an edit form similar to add benefit
}

async function viewDocument(id) {
    try {
        const response = await fetch(`${window.hrApp.baseURL}/api/training/documents/${id}`, {
            headers: window.hrApp.getHeaders()
        });
        
        if (response.ok) {
            const doc = await response.json();
            
            const modalHtml = `
                <div class="modal" id="viewDocumentModal" style="display: flex;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Document Details</h2>
                            <span class="close" onclick="document.getElementById('viewDocumentModal').remove()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <h3>${doc.document_name}</h3>
                            <p><strong>Employee:</strong> ${doc.employee_name || 'N/A'}</p>
                            <p><strong>Document Type:</strong> ${doc.document_type}</p>
                            <p><strong>Upload Date:</strong> ${doc.upload_date}</p>
                            <p><strong>File Path:</strong> ${doc.file_path || 'N/A'}</p>
                            <div class="mt-3">
                                <h4>Description</h4>
                                <p>${doc.description || 'No description available'}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('viewDocumentModal').remove()">Close</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    } catch (error) {
        console.error('Error loading document:', error);
        alert('Failed to load document details');
    }
}

async function deleteDocument(id) {
    if (confirm('Are you sure you want to delete this document?')) {
        try {
            const response = await fetch(`${window.hrApp.baseURL}/api/training/documents/${id}`, {
                method: 'DELETE',
                headers: window.hrApp.getHeaders()
            });
            
            if (response.ok) {
                alert('Document deleted successfully');
                window.hrApp.loadDocuments();
            } else {
                alert('Failed to delete document');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            alert('Failed to delete document');
        }
    }
}

async function completeTraining(enrollmentId) {
    if (confirm('Mark this training as completed?')) {
        try {
            const response = await fetch(`${window.hrApp.baseURL}/api/training/enrollments/${enrollmentId}/complete`, {
                method: 'PUT',
                headers: window.hrApp.getHeaders()
            });
            
            if (response.ok) {
                alert('Training marked as completed');
                window.hrApp.loadTrainingEnrollments();
            } else {
                alert('Failed to complete training');
            }
        } catch (error) {
            console.error('Error completing training:', error);
            alert('Failed to complete training');
        }
    }
}

// AI Assistant Functions
class AIAssistant {
    constructor(app) {
        this.app = app;
        this.chatHistory = [];
    }

    async sendQuery(question) {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/chat`, {
                method: 'POST',
                headers: {
                    ...this.app.getHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    context: { user_id: this.app.currentUser?.id }
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.chatHistory.push({
                    question: question,
                    answer: result.data.response,
                    timestamp: new Date()
                });
                return result.data;
            }
        } catch (error) {
            console.error('AI chat error:', error);
            return {
                response: "I'm having trouble connecting right now. Please try again later.",
                category: 'error'
            };
        }
    }

    async getPerformanceAnalysis(employeeId) {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/performance-analysis/${employeeId}`, {
                headers: this.app.getHeaders()
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.analysis;
            }
        } catch (error) {
            console.error('Performance analysis error:', error);
            return null;
        }
    }

    async getTrainingRecommendations(employeeId) {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/training-recommendations/${employeeId}`, {
                headers: this.app.getHeaders()
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.recommendations;
            }
        } catch (error) {
            console.error('Training recommendations error:', error);
            return null;
        }
    }

    async checkAttritionRisk(employeeId) {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/attrition-risk/${employeeId}`, {
                headers: this.app.getHeaders()
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.risk_analysis;
            }
        } catch (error) {
            console.error('Attrition risk error:', error);
            return null;
        }
    }

    async getDashboardInsights() {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/insights/dashboard`, {
                headers: this.app.getHeaders()
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.insights;
            }
        } catch (error) {
            console.error('Dashboard insights error:', error);
            return null;
        }
    }

    async askNaturalLanguageQuery(query) {
        try {
            const response = await fetch(`${this.app.baseURL}/api/ai/ask`, {
                method: 'POST',
                headers: {
                    ...this.app.getHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.response;
            }
        } catch (error) {
            console.error('NL query error:', error);
            return null;
        }
    }
}

// AI Chat Interface Functions
function showAIChatBot() {
    const chatHTML = `
        <div id="aiChatWidget" class="ai-chat-widget">
            <div class="chat-header">
                <h3>🤖 AI HR Assistant</h3>
                <button onclick="closeAIChat()" class="close-btn">×</button>
            </div>
            <div id="chatMessages" class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" id="aiChatInput" placeholder="Ask me anything about HR..." class="chat-input" />
                <button onclick="sendAIMessage()" class="send-btn">Send</button>
            </div>
            <div class="quick-questions">
                <button onclick="askQuickQuestion('How do I request leave?')" class="quick-btn">Request Leave</button>
                <button onclick="askQuickQuestion('What training programs are available?')" class="quick-btn">Training</button>
                <button onclick="askQuickQuestion('How do I check my payroll?')" class="quick-btn">Payroll</button>
            </div>
        </div>
        <style>
            .ai-chat-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 400px;
                height: 600px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                z-index: 1000;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 15px 15px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .chat-header h3 {
                margin: 0;
                font-size: 18px;
            }
            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 80%;
            }
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .ai-message {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
            }
            .chat-input-container {
                display: flex;
                padding: 15px;
                border-top: 1px solid #e0e0e0;
            }
            .chat-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 20px;
                margin-right: 10px;
            }
            .send-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                cursor: pointer;
            }
            .quick-questions {
                padding: 10px 15px;
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                border-top: 1px solid #e0e0e0;
            }
            .quick-btn {
                background: #f0f0f0;
                border: none;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                cursor: pointer;
            }
            .quick-btn:hover {
                background: #e0e0e0;
            }
        </style>
    `;
    
    document.body.insertAdjacentHTML('beforeend', chatHTML);
    
    // Add welcome message
    addAIMessage("Hello! I'm your AI HR Assistant. How can I help you today?");
    
    // Enter key to send
    document.getElementById('aiChatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAIMessage();
    });
}

function closeAIChat() {
    const widget = document.getElementById('aiChatWidget');
    if (widget) widget.remove();
}

async function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const question = input.value.trim();
    
    if (!question) return;
    
    // Add user message
    addUserMessage(question);
    input.value = '';
    
    // Get AI response
    const response = await window.aiAssistant.sendQuery(question);
    addAIMessage(response.response);
}

function askQuickQuestion(question) {
    document.getElementById('aiChatInput').value = question;
    sendAIMessage();
}

function addUserMessage(text) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addAIMessage(text) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add AI floating button
function addAIFloatingButton() {
    const buttonHTML = `
        <button id="aiFloatingBtn" onclick="showAIChatBot()" class="ai-floating-btn">
            🤖 AI Assistant
        </button>
        <style>
            .ai-floating-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 30px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                z-index: 999;
                transition: all 0.3s ease;
            }
            .ai-floating-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
        </style>
    `;
    
    document.body.insertAdjacentHTML('beforeend', buttonHTML);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.hrApp = new HRApp();
    window.aiAssistant = new AIAssistant(window.hrApp);
    
    // Add AI floating button after a short delay
    setTimeout(() => {
        if (!document.getElementById('aiFloatingBtn')) {
            addAIFloatingButton();
        }
    }, 2000);
});