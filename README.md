# SQL Database for Attendance System Python

A comprehensive Python package for managing an attendance system using SQLAlchemy ORM with a SQLite database backend.

## Overview

This package provides a robust solution for tracking employee attendance with features for managing identities and attendance records. The system uses SQLAlchemy for database operations and can be easily integrated into various Python applications.

## Installation

### Requirements

- Python 3.6+
- SQLAlchemy
- pytest (for running tests)

### Setup

1. Install the package dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the database connection in `config.py`:

```python
DATABASE_URL = "sqlite:///attendance.db"  # Default SQLite configuration
# For other database types (e.g., PostgreSQL):
# DATABASE_URL = "postgresql://username:password@localhost:5432/attendance_db"
```

3. Initialize the database:

```python
from src.api.easy_api import setup_database

# Only needed once at application startup
setup_database()
```

## Package Structure

```
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── easy_api.py         # Simplified API functions
│   ├── database/
│   │   ├── connection.py       # Database connection management
│   │   └── models.py           # SQLAlchemy ORM models
│   ├── services/
│   │   ├── identity_service.py     # Identity management services
│   │   └── attendance_service.py   # Attendance management services
│   └── utils/
└── tests/
    ├── test_identity.py        # Identity service tests
    └── test_attendance.py      # Attendance service tests
```

## API Reference

### Simplified API (Recommended)

The package offers a simplified API through the `src.api.easy_api` module, providing easy-to-use functions for common tasks without having to manage database sessions or service instances.

```python
from src.api.easy_api import (
    setup_database,
    create_employee,
    get_employee,
    record_check_in,
    record_check_out,
    get_attendance_history,
    EmployeeData  # Object-oriented approach
)
```

#### EmployeeData Class

The `EmployeeData` class provides an object-oriented approach to working with employee records:

```python
# Create employee object
employee = EmployeeData(
    name="Jane Doe",
    email="jane.doe@example.com",
    employee_id="EMP001",
    phone="555-1234"
)

# Convert from database model
employee = EmployeeData.from_identity(identity_model)

# Convert to dictionary
employee_dict = employee.to_dict()
```

#### Database Setup

- `setup_database()`: Initialize the database with all required tables

#### Employee Management

- `create_employee(name, email, employee_id, phone=None)`: Create a new employee
- `get_employee(employee_id=None, email=None)`: Get an employee by ID or email
- `update_employee(employee_id, name=None, email=None, phone=None)`: Update employee details
- `deactivate_employee(employee_id)`: Deactivate an employee (soft delete)
- `reactivate_employee(employee_id)`: Reactivate a previously deactivated employee
- `get_all_employees(include_inactive=False)`: Get all employees

#### Attendance Management

- `record_check_in(employee_id, check_in_time=None)`: Record employee check-in
- `record_check_out(employee_id, check_out_time=None)`: Record employee check-out
- `mark_attendance(employee_id, attendance_date=None, status="Present")`: Mark attendance for a date
- `get_attendance_history(employee_id, start_date=None, end_date=None)`: Get attendance history
- `get_attendance_report(report_date=None, include_inactive=False)`: Generate attendance report

### Advanced API

For more advanced usage, the package also provides direct access to the underlying services and models. 

#### Database Models

##### Identity

The `Identity` model represents an employee or user in the system.

**Attributes:**
- `id`: Primary key
- `name`: Employee name
- `email`: Unique email address
- `phone`: Optional phone number
- `employee_id`: Unique employee identifier
- `created_at`: Creation timestamp
- `is_active`: Boolean flag for active status

##### Attendance

The `Attendance` model represents attendance records for identities.

**Attributes:**
- `id`: Primary key
- `identity_id`: Foreign key to Identity
- `date`: Date of attendance
- `check_in`: Check-in timestamp
- `check_out`: Check-out timestamp
- `status`: Status indicator (Present, Absent, Late, etc.)

#### Identity Service

The `IdentityService` class provides methods for managing employee identities.

```python
from sqlalchemy.orm import Session
from src.services.identity_service import IdentityService

# Create an instance with a database session
db_session = Session()
identity_service = IdentityService(db_session)
```

**Available Methods:**

- `get_all_identities(skip=0, limit=100)`: Retrieve all identities with pagination
- `get_identity_by_id(identity_id)`: Retrieve an identity by ID
- `get_identity_by_employee_id(employee_id)`: Retrieve an identity by employee ID
- `get_identity_by_email(email)`: Retrieve an identity by email
- `create_identity(name, email, employee_id, phone=None, is_active=True)`: Create a new identity
- `create_identity_from_object(employee_data)`: Create a new identity from an employee data object
- `update_identity(identity_id, **kwargs)`: Update an identity's attributes
- `update_identity_from_object(identity_id, employee_data)`: Update an identity using an employee data object
- `deactivate_identity(identity_id)`: Mark an identity as inactive
- `reactivate_identity(identity_id)`: Reactivate a previously deactivated identity
- `delete_identity(identity_id)`: Permanently delete an identity

#### Attendance Service

The `AttendanceService` class provides methods for managing attendance records.

```python
from sqlalchemy.orm import Session
from src.services.attendance_service import AttendanceService

# Create an instance with a database session
db_session = Session()
attendance_service = AttendanceService(db_session)
```

**Available Methods:**

- `get_attendance_by_id(attendance_id)`: Retrieve attendance by ID
- `get_attendance_by_date(attendance_date)`: Get all attendance records for a date
- `get_attendance_by_identity(identity_id, skip=0, limit=100)`: Get attendance for a specific identity
- `get_attendance_by_date_range(identity_id, start_date, end_date)`: Get attendance within a date range
- `create_attendance(identity_id, attendance_date, status=None)`: Create a new attendance record
- `record_check_in(identity_id, attendance_date=None, check_in_time=None)`: Record check-in event
- `record_check_out(identity_id, attendance_date=None, check_out_time=None)`: Record check-out event
- `update_attendance_status(attendance_id, status)`: Update attendance status
- `delete_attendance(attendance_id)`: Delete an attendance record

## Usage Examples

### Using the Simplified API with Object-Oriented Approach (Recommended)

```python
from src.api.easy_api import (
    setup_database,
    create_employee,
    get_employee,
    record_check_in,
    record_check_out,
    get_attendance_history,
    mark_attendance,
    get_attendance_report,
    EmployeeData
)
from datetime import datetime, timedelta

# Setup the database
setup_database()

# Create employee objects
first_employee = EmployeeData(
    name="Jane Doe",
    email="jane.doe@example.com",
    employee_id="EMP002",
    phone="555-6789"
)

second_employee = EmployeeData(
    name="John Smith",
    email="john.smith@example.com",
    employee_id="EMP003",
    phone="555-1234"
)

# Helper function to register employees
def register_employee(employee_data):
    try:
        # Try to create a new employee
        employee = create_employee(
            name=employee_data.name,
            email=employee_data.email,
            employee_id=employee_data.employee_id,
            phone=employee_data.phone
        )
        return employee
    except ValueError:
        # Employee might already exist
        employee = get_employee(employee_id=employee_data.employee_id)
        if employee:
            return employee
        else:
            raise ValueError(f"Could not create/retrieve employee {employee_data.employee_id}")

# Register employees
employee1 = register_employee(first_employee)
employee2 = register_employee(second_employee)

# Record check-in and check-out for first employee
check_in_data = record_check_in(employee_id=employee1.employee_id)
print(f"Check-in recorded at: {check_in_data['check_in']}")

# Record check-out (8 hours later)
check_out_time = datetime.now() + timedelta(hours=8)
check_out_data = record_check_out(
    employee_id=employee1.employee_id,
    check_out_time=check_out_time
)
print(f"Check-out recorded at: {check_out_data['check_out']}")

# Mark attendance for second employee without check-in/check-out details
mark_attendance(
    employee_id=employee2.employee_id,
    status="Present"
)

# Get attendance history
history = get_attendance_history(employee_id=employee1.employee_id)
for record in history:
    print(f"Date: {record['date']}, Status: {record['status']}")
    if record['hours_worked']:
        print(f"Hours worked: {record['hours_worked']}")

# Generate an attendance report for today
report = get_attendance_report()
print(f"Present employees: {len(report['present'])}")
print(f"Absent employees: {len(report['absent'])}")
```

### Using the Simplified API (Procedural Style)

```python
from src.api.easy_api import (
    setup_database,
    create_employee,
    get_employee,
    record_check_in,
    record_check_out,
    get_attendance_history,
    get_attendance_report
)
from datetime import datetime, timedelta

# Setup the database (only needed once)
setup_database()

# Create a new employee
try:
    employee = create_employee(
        name="John Smith", 
        email="john.smith@example.com", 
        employee_id="EMP003", 
        phone="555-4321"
    )
    print(f"Created employee: {employee}")
except ValueError as e:
    # Handle the case where the employee might already exist
    employee = get_employee(employee_id="EMP003")
    print(f"Found existing employee: {employee}")

# Record check-in
check_in_data = record_check_in(employee_id="EMP003")
print(f"Check-in recorded at: {check_in_data['check_in']}")

# Record check-out (8 hours later)
check_out_time = datetime.now() + timedelta(hours=8)
check_out_data = record_check_out(employee_id="EMP003", check_out_time=check_out_time)
print(f"Check-out recorded at: {check_out_data['check_out']}")

# Get attendance history
history = get_attendance_history(employee_id="EMP003")
for record in history:
    print(f"Date: {record['date']}, Status: {record['status']}")
    if record['hours_worked']:
        print(f"Hours worked: {record['hours_worked']}")

# Generate an attendance report for today
report = get_attendance_report()
print(f"Present employees: {len(report['present'])}")
print(f"Absent employees: {len(report['absent'])}")
```

### Advanced Object-Oriented Approach with Service Classes

For more advanced usage, you can work directly with the service classes:

```python
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.services.identity_service import IdentityService

# Custom employee data class
class EmployeeData:
    def __init__(self, name, email, employee_id, phone=None, is_active=True):
        self.name = name
        self.email = email
        self.employee_id = employee_id
        self.phone = phone
        self.is_active = is_active
        
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'employee_id': self.employee_id,
            'phone': self.phone,
            'is_active': self.is_active
        }
        
    @classmethod
    def from_identity(cls, identity):
        """Create an EmployeeData object from an Identity database model"""
        return cls(
            name=identity.name,
            email=identity.email,
            employee_id=identity.employee_id,
            phone=identity.phone,
            is_active=identity.is_active
        )

# Create a database session
db = SessionLocal()
identity_service = IdentityService(db)

# Create a new employee object
employee_data = EmployeeData(
    name="John Doe",
    email="john.doe@example.com",
    employee_id="EMP001",
    phone="555-123-4567"
)

# Method 1: Create identity directly from the employee object
identity = identity_service.create_identity_from_object(employee_data)

# Method 2: Create identity by unpacking the employee object
# identity = identity_service.create_identity(**employee_data.to_dict())

# Update an employee's information with a new object
updated_data = EmployeeData(
    name="John M. Doe",
    email="john.doe@example.com",
    employee_id="EMP001",
    phone="555-987-6543"
)
updated_identity = identity_service.update_identity_from_object(identity.id, updated_data)

# Find an identity and convert back to an employee object
db_identity = identity_service.get_identity_by_employee_id("EMP001")
retrieved_employee = EmployeeData.from_identity(db_identity)
```

### Managing Attendance Records (Advanced)

```python
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.services.attendance_service import AttendanceService

# Create a database session
db = SessionLocal()
attendance_service = AttendanceService(db)

# Record a check-in for today
attendance = attendance_service.record_check_in(
    identity_id=1,  # Employee ID from the identity table
    check_in_time=datetime.now()
)

# Record a check-out
attendance = attendance_service.record_check_out(
    identity_id=1,
    check_out_time=datetime.now() + timedelta(hours=8)
)

# Create an attendance record for a specific date
custom_attendance = attendance_service.create_attendance(
    identity_id=1,
    attendance_date=date(2025, 3, 26),
    status="Present"
)

# Get attendance history for an employee
history = attendance_service.get_attendance_by_identity(1)

# Get attendance within a date range
date_range = attendance_service.get_attendance_by_date_range(
    identity_id=1,
    start_date=date(2025, 3, 1),
    end_date=date(2025, 3, 31)
)
```

## Database Connection Management

The package provides utilities for managing database connections:

```python
from src.database.connection import get_db, init_db, engine, SessionLocal

# Initialize the database (create tables)
init_db()

# Get a database session
db = next(get_db())
try:
    # Perform database operations
    pass
finally:
    db.close()

# Alternative: using context manager
with SessionLocal() as db:
    # Perform database operations
    pass
```

## Testing

Run the test suite using pytest:

```bash
pytest
```

## Quick Start Guide

To quickly get started with the attendance system:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the example script to see the API in action:
   ```bash
   python easy_example.py
   ```

3. Integrate the package into your own application by importing from the `src.api.easy_api` module.

## License

This project is licensed under the terms of the LICENSE file included in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.