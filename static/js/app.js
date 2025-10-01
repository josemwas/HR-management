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

// Placeholder functions for actions (to be implemented)
function editEmployee(id) {
    alert(`Edit employee ${id} - Feature to be implemented`);
}

function viewJob(id) {
    alert(`View job ${id} - Feature to be implemented`);
}

function editJob(id) {
    alert(`Edit job ${id} - Feature to be implemented`);
}

function viewApplicant(id) {
    alert(`View applicant ${id} - Feature to be implemented`);
}

function updateApplicantStatus(id, status) {
    alert(`Update applicant ${id} status to ${status} - Feature to be implemented`);
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

function showTrainingPrograms() {
    document.getElementById('trainingPrograms').style.display = 'block';
    document.getElementById('trainingEnrollments').style.display = 'none';
    
    // Update tab buttons
    document.querySelectorAll('.training-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    app.loadTrainingPrograms();
}

function showTrainingEnrollments() {
    document.getElementById('trainingPrograms').style.display = 'none';
    document.getElementById('trainingEnrollments').style.display = 'block';
    
    // Update tab buttons
    document.querySelectorAll('.training-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
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
function exportReports() {
    alert('Export functionality - Feature to be implemented with CSV/PDF export');
}

function generateEmployeeReport() {
    app.generateReport('employees');
}

function generateAttendanceReport() {
    app.generateReport('attendance');
}

function generateLeaveReport() {
    app.generateReport('leaves');
}

function generatePayrollReport() {
    app.generateReport('payroll');
}

function generatePerformanceReport() {
    app.generateReport('performance');
}

function generateTrainingReport() {
    app.generateReport('training');
}

function viewReview(id) {
    alert(`View review ${id} - Feature to be implemented`);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.hrApp = new HRApp();
});