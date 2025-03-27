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
from src.database.connection import init_db

init_db()  # Creates all necessary tables
```

## Package Structure

```
├── src/
│   ├── database/
│   │   ├── connection.py     # Database connection management
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── services/
│   │   ├── identity_service.py    # Identity management services
│   │   └── attendance_service.py  # Attendance management services
│   └── utils/
└── tests/
    ├── test_identity.py      # Identity service tests
    └── test_attendance.py    # Attendance service tests
```

## API Reference

### Database Models

#### Identity

The `Identity` model represents an employee or user in the system.

**Attributes:**
- `id`: Primary key
- `name`: Employee name
- `email`: Unique email address
- `phone`: Optional phone number
- `employee_id`: Unique employee identifier
- `created_at`: Creation timestamp
- `is_active`: Boolean flag for active status

#### Attendance

The `Attendance` model represents attendance records for identities.

**Attributes:**
- `id`: Primary key
- `identity_id`: Foreign key to Identity
- `date`: Date of attendance
- `check_in`: Check-in timestamp
- `check_out`: Check-out timestamp
- `status`: Status indicator (Present, Absent, Late, etc.)

### Identity Service

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
- `create_identity(name, email, employee_id, phone=None)`: Create a new identity
- `update_identity(identity_id, **kwargs)`: Update an identity's attributes
- `deactivate_identity(identity_id)`: Mark an identity as inactive
- `reactivate_identity(identity_id)`: Reactivate a previously deactivated identity
- `delete_identity(identity_id)`: Permanently delete an identity

### Attendance Service

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

### Creating and Managing Identities

```python
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.services.identity_service import IdentityService

# Create a database session
db = SessionLocal()
identity_service = IdentityService(db)

# Create a new identity
employee = identity_service.create_identity(
    name="John Doe",
    email="john.doe@example.com",
    employee_id="EMP001",
    phone="555-123-4567"
)

# Update an identity
updated_employee = identity_service.update_identity(
    employee.id,
    name="John M. Doe",
    phone="555-987-6543"
)

# Find an identity by employee ID
found_employee = identity_service.get_identity_by_employee_id("EMP001")

# Deactivate an identity
identity_service.deactivate_identity(employee.id)
```

### Managing Attendance Records

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

## License

This project is licensed under the terms of the LICENSE file included in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.