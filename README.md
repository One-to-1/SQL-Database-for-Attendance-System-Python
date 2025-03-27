# SQL Database for Attendance System Python

A comprehensive Python package for managing an attendance system using SQLAlchemy ORM with a SQLite database backend.

## Overview

This package provides a robust solution for tracking student attendance with features for managing identities and attendance records. The system uses SQLAlchemy for database operations and can be easily integrated into various Python applications.

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
    ├── test_easy_api.py        # API tests
    └── test_attendance.py      # Attendance service tests
```

## API Reference

### Simplified API (Recommended)

The package offers a simplified API through the `src.api.easy_api` module, providing easy-to-use functions for common tasks without having to manage database sessions or service instances.

```python
from src.api.easy_api import (
    setup_database,
    create_student,
    get_student,
    record_check_in,
    record_check_out,
    get_attendance_history,
    StudentData  # Object-oriented approach
)
```

#### StudentData Class

The `StudentData` class provides an object-oriented approach to working with student records:

```python
# Create student object
student = StudentData(
    name="Jane Doe",
    email="jane.doe@example.com",
    student_id="EMP001",
    phone="555-1234"
)

# Convert from database model
student = StudentData.from_identity(identity_model)

# Convert to dictionary
student_dict = student.to_dict()
```

#### Database Setup

- `setup_database()`: Initialize the database with all required tables

#### Student Management

- `create_student(name, email, student_id, phone=None)`: Create a new student
- `get_student(student_id=None, email=None)`: Get an student by ID or email
- `update_student(student_id, name=None, email=None, phone=None)`: Update student details
- `deactivate_student(student_id)`: Deactivate an student (soft delete)
- `reactivate_student(student_id)`: Reactivate a previously deactivated student
- `get_all_students(include_inactive=False)`: Get all students

#### Attendance Management

- `record_check_in(student_id, check_in_time=None)`: Record student check-in
- `record_check_out(student_id, check_out_time=None)`: Record student check-out
- `mark_attendance(student_id, attendance_date=None, status="Present")`: Mark attendance for a date
- `get_attendance_history(student_id, start_date=None, end_date=None)`: Get attendance history
- `get_attendance_report(report_date=None, include_inactive=False)`: Generate attendance report

### Advanced API

For more advanced usage, the package also provides direct access to the underlying services and models. 

#### Database Models

##### Identity

The `Identity` model represents an student or user in the system.

**Attributes:**
- `id`: Primary key
- `name`: Student name
- `email`: Unique email address
- `phone`: Optional phone number
- `student_id`: Unique student identifier
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

The `IdentityService` class provides methods for managing student identities.

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
- `get_identity_by_student_id(student_id)`: Retrieve an identity by student ID
- `get_identity_by_email(email)`: Retrieve an identity by email
- `create_identity(name, email, student_id, phone=None, is_active=True)`: Create a new identity
- `create_identity_from_object(student_data)`: Create a new identity from an student data object
- `update_identity(identity_id, **kwargs)`: Update an identity's attributes
- `update_identity_from_object(identity_id, student_data)`: Update an identity using an student data object
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
    create_student,
    get_student,
    record_check_in,
    record_check_out,
    get_attendance_history,
    mark_attendance,
    get_attendance_report,
    StudentData
)
from datetime import datetime, timedelta

# Setup the database
setup_database()

# Create student objects
first_student = StudentData(
    name="Jane Doe",
    email="jane.doe@example.com",
    student_id="EMP002",
    phone="555-6789"
)

second_student = StudentData(
    name="John Smith",
    email="john.smith@example.com",
    student_id="EMP003",
    phone="555-1234"
)

# Helper function to register students
def register_student(student_data):
    try:
        # Try to create a new student
        student = create_student(
            name=student_data.name,
            email=student_data.email,
            student_id=student_data.student_id,
            phone=student_data.phone
        )
        return student
    except ValueError:
        # Student might already exist
        student = get_student(student_id=student_data.student_id)
        if student:
            return student
        else:
            raise ValueError(f"Could not create/retrieve student {student_data.student_id}")

# Register students
student1 = register_student(first_student)
student2 = register_student(second_student)

# Record check-in and check-out for first student
check_in_data = record_check_in(student_id=student1.student_id)
print(f"Check-in recorded at: {check_in_data['check_in']}")

# Record check-out (8 hours later)
check_out_time = datetime.now() + timedelta(hours=8)
check_out_data = record_check_out(
    student_id=student1.student_id,
    check_out_time=check_out_time
)
print(f"Check-out recorded at: {check_out_data['check_out']}")

# Mark attendance for second student without check-in/check-out details
mark_attendance(
    student_id=student2.student_id,
    status="Present"
)

# Get attendance history
history = get_attendance_history(student_id=student1.student_id)
for record in history:
    print(f"Date: {record['date']}, Status: {record['status']}")
    if record['hours_worked']:
        print(f"Hours worked: {record['hours_worked']}")

# Generate an attendance report for today
report = get_attendance_report()
print(f"Present students: {len(report['present'])}")
print(f"Absent students: {len(report['absent'])}")
```

### Using the Simplified API (Procedural Style)

```python
from src.api.easy_api import (
    setup_database,
    create_student,
    get_student,
    record_check_in,
    record_check_out,
    get_attendance_history,
    get_attendance_report
)
from datetime import datetime, timedelta

# Setup the database (only needed once)
setup_database()

# Create a new student
try:
    student = create_student(
        name="John Smith", 
        email="john.smith@example.com", 
        student_id="EMP003", 
        phone="555-4321"
    )
    print(f"Created student: {student}")
except ValueError as e:
    # Handle the case where the student might already exist
    student = get_student(student_id="EMP003")
    print(f"Found existing student: {student}")

# Record check-in
check_in_data = record_check_in(student_id="EMP003")
print(f"Check-in recorded at: {check_in_data['check_in']}")

# Record check-out (8 hours later)
check_out_time = datetime.now() + timedelta(hours=8)
check_out_data = record_check_out(student_id="EMP003", check_out_time=check_out_time)
print(f"Check-out recorded at: {check_out_data['check_out']}")

# Get attendance history
history = get_attendance_history(student_id="EMP003")
for record in history:
    print(f"Date: {record['date']}, Status: {record['status']}")
    if record['hours_worked']:
        print(f"Hours worked: {record['hours_worked']}")

# Generate an attendance report for today
report = get_attendance_report()
print(f"Present students: {len(report['present'])}")
print(f"Absent students: {len(report['absent'])}")
```

### Advanced Object-Oriented Approach with Service Classes

For more advanced usage, you can work directly with the service classes:

```python
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.services.identity_service import IdentityService

# Custom student data class
class StudentData:
    def __init__(self, name, email, student_id, phone=None, is_active=True):
        self.name = name
        self.email = email
        self.student_id = student_id
        self.phone = phone
        self.is_active = is_active
        
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'student_id': self.student_id,
            'phone': self.phone,
            'is_active': self.is_active
        }
        
    @classmethod
    def from_identity(cls, identity):
        """Create an StudentData object from an Identity database model"""
        return cls(
            name=identity.name,
            email=identity.email,
            student_id=identity.student_id,
            phone=identity.phone,
            is_active=identity.is_active
        )

# Create a database session
db = SessionLocal()
identity_service = IdentityService(db)

# Create a new student object
student_data = StudentData(
    name="John Doe",
    email="john.doe@example.com",
    student_id="EMP001",
    phone="555-123-4567"
)

# Method 1: Create identity directly from the student object
identity = identity_service.create_identity_from_object(student_data)

# Method 2: Create identity by unpacking the student object
# identity = identity_service.create_identity(**student_data.to_dict())

# Update an student's information with a new object
updated_data = StudentData(
    name="John M. Doe",
    email="john.doe@example.com",
    student_id="EMP001",
    phone="555-987-6543"
)
updated_identity = identity_service.update_identity_from_object(identity.id, updated_data)

# Find an identity and convert back to an student object
db_identity = identity_service.get_identity_by_student_id("EMP001")
retrieved_student = StudentData.from_identity(db_identity)
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
    identity_id=1,  # Student ID from the identity table
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

# Get attendance history for an student
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