# SQL Database for Attendance System (Python)

A robust and modular database management system specifically designed for attendance tracking applications. This system provides a flexible database layer that can be easily integrated with any attendance tracking frontend or application.

## Overview

This project implements a complete database management system for attendance tracking with comprehensive APIs for:
- Managing identities (employees, students, etc.)
- Recording and querying attendance data
- Handling check-ins and check-outs
- Supporting various attendance statuses

Built with modern Python and SQLAlchemy, this system offers a reliable foundation for any attendance tracking needs.

## Features

- **Identity Management**
  - Create, update, and delete user identities
  - Query identities by ID, email, or employee ID
  - Support for soft-delete (deactivation) and reactivation

- **Attendance Tracking**
  - Record daily attendance with customizable statuses
  - Support for check-in/check-out timestamps
  - Query attendance by date, identity, or date ranges

- **Flexible Storage**
  - SQLite support for development and small deployments
  - PostgreSQL configuration available for production environments
  - Easy configuration via config.py

- **Tested and Reliable**
  - Comprehensive test suite with pytest
  - High test coverage for core functionality

## Project Structure

```
attendance-dbms/
├── config.py                 # Database configuration
├── requirements.txt          # Project dependencies
├── README.md                 # Module documentation
├── src/
│   ├── __init__.py           # Package initialization
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py     # Database connection management
│   │   └── models.py         # SQLAlchemy models (Identity, Attendance)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── identity_service.py    # Identity management logic
│   │   └── attendance_service.py  # Attendance tracking logic
│   └── utils/
│       ├── __init__.py
│       └── validators.py     # Data validation utilities (optional)
└── tests/
    ├── __init__.py
    ├── test_identity.py      # Tests for identity service
    └── test_attendance.py    # Tests for attendance service
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/SQL-Database-for-Attendance-System-Python.git
   cd SQL-Database-for-Attendance-System-Python
   ```

2. Install dependencies:
   ```bash
   pip install -r attendance-dbms/requirements.txt
   ```

3. Configure database settings in `attendance-dbms/config.py` (SQLite is configured by default)

## Technical Implementation

### Database Models

The system uses two primary models:

1. **Identity Model**
   - Stores user/employee information
   - Fields: id, name, email, phone, employee_id, created_at, is_active
   - Relationships: One-to-many with Attendance

2. **Attendance Model**
   - Records daily attendance information
   - Fields: id, identity_id, date, check_in, check_out, status
   - Relationships: Many-to-one with Identity

### Service Layer

The system implements a service-oriented architecture with two primary services:

1. **IdentityService**
   - Methods for creating, updating, querying, and deleting identities
   - Support for both soft-delete (deactivation) and hard-delete operations
   - Efficient identity lookup by various attributes (ID, email, employee_id)

2. **AttendanceService**
   - Methods for recording and managing attendance
   - Support for check-in and check-out operations
   - Attendance reporting by date, identity, or date ranges

## Usage Examples

### Initialize Database

```python
from attendance_dbms.src import initialize

# Create all tables
initialize()
```

### Managing Identities

```python
from attendance_dbms.src.database.connection import get_db
from attendance_dbms.src.services.identity_service import IdentityService

# Get database session
db = next(get_db())

# Create identity service
identity_service = IdentityService(db)

# Create a new identity
new_employee = identity_service.create_identity(
    name="John Doe",
    email="john.doe@example.com",
    employee_id="EMP001",
    phone="555-1234"
)

# Find by employee ID
employee = identity_service.get_identity_by_employee_id("EMP001")

# Update identity
identity_service.update_identity(
    employee.id,
    name="John D. Doe",
    phone="555-9876"
)

# Deactivate an identity
identity_service.deactivate_identity(employee.id)
```

### Managing Attendance

```python
from datetime import date, datetime
from attendance_dbms.src.services.attendance_service import AttendanceService

# Create attendance service
attendance_service = AttendanceService(db)

# Record attendance for today
attendance = attendance_service.create_attendance(
    identity_id=employee.id,
    attendance_date=date.today(),
    status="Present"
)

# Record check-in
attendance_service.record_check_in(
    identity_id=employee.id,
    check_in_time=datetime.now()
)

# Record check-out
attendance_service.record_check_out(
    identity_id=employee.id,
    check_out_time=datetime.now()
)

# Get attendance by date
today_attendance = attendance_service.get_attendance_by_date(date.today())

# Get attendance history for an employee
history = attendance_service.get_attendance_by_identity(employee.id)

# Get attendance for a date range
from datetime import timedelta
start_date = date.today() - timedelta(days=7)
end_date = date.today()
weekly_attendance = attendance_service.get_attendance_by_date_range(
    identity_id=employee.id,
    start_date=start_date,
    end_date=end_date
)
```

## Integration with Other Systems

This database management system is designed to integrate easily with other applications:

1. **Web Applications**
   - Integrate with Flask/Django as a database layer
   - Use the service layer directly from your routes/views

2. **Desktop Applications**
   - Import as a module into any Python desktop application
   - Use the service classes to manage attendance data

3. **APIs**
   - Build REST API endpoints around the service layer
   - Expose attendance functionality to external systems

## Running Tests

```bash
cd attendance-dbms
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.