# Contributing to HR Management System

Thank you for your interest in contributing to the HR Management System! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/HR-management.git
   cd HR-management
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize test database:**
   ```bash
   python init_sample_data.py
   ```

4. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

When suggesting enhancements:
- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- List any potential drawbacks or considerations

### Contributing Code

Areas where contributions are especially welcome:
- Bug fixes
- New features
- Documentation improvements
- Test coverage improvements
- Performance optimizations
- UI/UX improvements

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 79 characters for code
- Maximum line length of 72 characters for docstrings/comments
- Use descriptive variable names
- Add docstrings to all functions and classes

Example:
```python
def calculate_net_salary(basic_salary, allowances, deductions):
    """
    Calculate net salary based on components.
    
    Args:
        basic_salary (float): Base salary amount
        allowances (float): Total allowances
        deductions (float): Total deductions
        
    Returns:
        float: Net salary after allowances and deductions
    """
    return basic_salary + allowances - deductions
```

### Code Structure

- Keep functions small and focused
- Use meaningful names for variables and functions
- Avoid deep nesting (max 3 levels)
- Add comments for complex logic
- Follow the existing project structure

### Database Models

- Use descriptive field names
- Add appropriate constraints (nullable, unique, etc.)
- Include relationships where appropriate
- Add `to_dict()` method for serialization

### API Endpoints

- Follow RESTful conventions
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Return consistent JSON responses
- Include proper error handling
- Add request validation

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Write tests for bug fixes
- Follow the existing test structure
- Use descriptive test names
- Include both positive and negative test cases

Example:
```python
def test_create_employee_success(client, auth_headers):
    """Test successful employee creation with valid data"""
    response = client.post('/api/employees',
                          headers=auth_headers,
                          json={...})
    assert response.status_code == 201
    assert 'id' in response.json()

def test_create_employee_duplicate_email(client, auth_headers):
    """Test employee creation fails with duplicate email"""
    response = client.post('/api/employees',
                          headers=auth_headers,
                          json={...})
    assert response.status_code == 400
    assert 'error' in response.json()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_employees.py

# Run specific test
pytest tests/test_employees.py::test_create_employee
```

### Test Coverage

- Aim for at least 80% code coverage
- Test all critical paths
- Test edge cases
- Test error handling

## Pull Request Process

1. **Update your fork:**
   ```bash
   git remote add upstream https://github.com/josemwas/HR-management.git
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes:**
   - Write clear, concise commit messages
   - Keep commits focused and atomic
   - Run tests before committing

3. **Push your changes:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request:**
   - Provide a clear title and description
   - Reference any related issues
   - Describe what your changes do
   - Include screenshots for UI changes
   - Ensure all tests pass
   - Request review from maintainers

### Pull Request Checklist

Before submitting a pull request, ensure:
- [ ] Code follows the style guidelines
- [ ] All tests pass
- [ ] New tests are added for new features
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Code is properly formatted
- [ ] All files have appropriate headers

## Development Workflow

1. **Choose an issue** or create a new one
2. **Assign yourself** to the issue
3. **Create a branch** from main
4. **Make changes** and commit regularly
5. **Write/update tests**
6. **Update documentation**
7. **Run tests** and fix any failures
8. **Push changes** to your fork
9. **Create Pull Request**
10. **Address review comments**
11. **Merge** after approval

## Documentation

When adding features:
- Update API.md with new endpoints
- Update FEATURES.md with feature description
- Add inline code comments
- Update README.md if needed
- Add examples if helpful

## Questions?

- Check existing issues and pull requests
- Read the documentation in the `docs/` folder
- Open a new issue for questions
- Be patient and respectful

## Recognition

Contributors will be:
- Listed in the project README
- Acknowledged in release notes
- Credited in commit history

Thank you for contributing to HR Management System! 🎉
