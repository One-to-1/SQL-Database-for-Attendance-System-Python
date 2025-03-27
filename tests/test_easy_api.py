import pytest
import sys
import os
from datetime import date, datetime, timedelta
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.database.connection import Base
from src.database.models import Identity, Attendance
from src.api.easy_api import (
    setup_database, get_session, EmployeeData,
    create_employee, get_employee, update_employee,
    deactivate_employee, reactivate_employee, get_all_employees,
    record_check_in, record_check_out, get_attendance_history,
    mark_attendance, get_attendance_report, _calculate_hours_worked
)


# Set up an in-memory SQLite database for testing
@pytest.fixture
def setup_test_db():
    # Create an engine that stores data in memory
    engine = create_engine("sqlite:///:memory:")
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Patch the get_db function to use our test database
    with patch("src.api.easy_api.engine", engine):
        with patch("src.api.easy_api.get_db", lambda: get_db_override(engine)):
            yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(engine)


def get_db_override(engine):
    """Override get_db for testing purposes"""
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_employee(setup_test_db):
    """Create a sample employee for testing"""
    employee = create_employee(
        name="John Doe",
        email="john.doe@example.com",
        employee_id="EMP001",
        phone="555-1234"
    )
    return employee


@pytest.fixture
def sample_employee_with_attendance(setup_test_db, sample_employee):
    """Create a sample employee with attendance records"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Create attendance for today and yesterday
    mark_attendance(
        employee_id=sample_employee.employee_id,
        attendance_date=yesterday,
        status="Present"
    )
    
    mark_attendance(
        employee_id=sample_employee.employee_id,
        attendance_date=today,
        status="Present"
    )
    
    return sample_employee


class TestDatabaseSetup:
    def test_setup_database(self, setup_test_db):
        """Test that database setup works correctly"""
        result = setup_database()
        assert result is True


class TestEmployeeDataClass:
    def test_employee_data_init(self):
        """Test EmployeeData initialization"""
        emp = EmployeeData(
            name="Test User",
            email="test@example.com",
            employee_id="EMP123",
            phone="555-5555"
        )
        
        assert emp.name == "Test User"
        assert emp.email == "test@example.com"
        assert emp.employee_id == "EMP123"
        assert emp.phone == "555-5555"
        assert emp.is_active is True
    
    def test_to_dict(self):
        """Test EmployeeData to_dict method"""
        emp = EmployeeData(
            name="Test User",
            email="test@example.com",
            employee_id="EMP123",
            phone="555-5555"
        )
        
        data_dict = emp.to_dict()
        assert data_dict["name"] == "Test User"
        assert data_dict["email"] == "test@example.com"
        assert data_dict["employee_id"] == "EMP123"
        assert data_dict["phone"] == "555-5555"
        assert data_dict["is_active"] is True
    
    def test_str_representation(self):
        """Test EmployeeData string representation"""
        emp = EmployeeData(
            name="Test User",
            email="test@example.com",
            employee_id="EMP123"
        )
        
        assert str(emp) == "Employee: Test User (EMP123)"


class TestEmployeeManagement:
    def test_create_employee(self, setup_test_db):
        """Test creating a new employee"""
        employee = create_employee(
            name="Jane Doe",
            email="jane.doe@example.com",
            employee_id="EMP002",
            phone="555-5678"
        )
        
        assert employee.name == "Jane Doe"
        assert employee.email == "jane.doe@example.com"
        assert employee.employee_id == "EMP002"
        assert employee.phone == "555-5678"
        assert employee.is_active is True
    
    def test_create_duplicate_employee(self, setup_test_db, sample_employee):
        """Test creating an employee with duplicate email raises error"""
        with pytest.raises(ValueError):
            create_employee(
                name="Another Person",
                email=sample_employee.email,  # Same email as existing employee
                employee_id="EMP003",
                phone="555-0000"
            )
    
    def test_get_employee_by_id(self, setup_test_db, sample_employee):
        """Test getting an employee by ID"""
        employee = get_employee(employee_id=sample_employee.employee_id)
        
        assert employee is not None
        assert employee.name == sample_employee.name
        assert employee.email == sample_employee.email
        assert employee.employee_id == sample_employee.employee_id
    
    def test_get_employee_by_email(self, setup_test_db, sample_employee):
        """Test getting an employee by email"""
        employee = get_employee(email=sample_employee.email)
        
        assert employee is not None
        assert employee.name == sample_employee.name
        assert employee.email == sample_employee.email
        assert employee.employee_id == sample_employee.employee_id
    
    def test_get_nonexistent_employee(self, setup_test_db):
        """Test getting a non-existent employee returns None"""
        employee = get_employee(employee_id="NOTFOUND")
        assert employee is None
        
        employee = get_employee(email="notfound@example.com")
        assert employee is None
    
    def test_get_employee_with_no_params(self, setup_test_db):
        """Test getting an employee with no parameters raises error"""
        with pytest.raises(ValueError):
            get_employee()
    
    def test_update_employee(self, setup_test_db, sample_employee):
        """Test updating an employee's details"""
        updated = update_employee(
            employee_id=sample_employee.employee_id,
            name="John Updated",
            email="john.updated@example.com",
            phone="555-9999"
        )
        
        assert updated is not None
        assert updated.name == "John Updated"
        assert updated.email == "john.updated@example.com"
        assert updated.phone == "555-9999"
        assert updated.employee_id == sample_employee.employee_id
    
    def test_update_nonexistent_employee(self, setup_test_db):
        """Test updating a non-existent employee returns None"""
        updated = update_employee(
            employee_id="NOTFOUND",
            name="Nobody"
        )
        assert updated is None
    
    def test_deactivate_employee(self, setup_test_db, sample_employee):
        """Test deactivating an employee"""
        result = deactivate_employee(sample_employee.employee_id)
        assert result is True
        
        # Verify the employee is deactivated
        employee = get_employee(employee_id=sample_employee.employee_id)
        assert employee.is_active is False
    
    def test_deactivate_nonexistent_employee(self, setup_test_db):
        """Test deactivating a non-existent employee returns False"""
        result = deactivate_employee("NOTFOUND")
        assert result is False
    
    def test_reactivate_employee(self, setup_test_db, sample_employee):
        """Test reactivating an employee"""
        # First deactivate
        deactivate_employee(sample_employee.employee_id)
        
        # Then reactivate
        result = reactivate_employee(sample_employee.employee_id)
        assert result is True
        
        # Verify the employee is reactivated
        employee = get_employee(employee_id=sample_employee.employee_id)
        assert employee.is_active is True
    
    def test_reactivate_nonexistent_employee(self, setup_test_db):
        """Test reactivating a non-existent employee returns False"""
        result = reactivate_employee("NOTFOUND")
        assert result is False
    
    def test_get_all_employees(self, setup_test_db):
        """Test getting all employees"""
        # Create some employees
        create_employee(
            name="Employee 1",
            email="emp1@example.com",
            employee_id="EMP001"
        )
        create_employee(
            name="Employee 2",
            email="emp2@example.com",
            employee_id="EMP002"
        )
        
        # Deactivate one employee
        deactivate_employee("EMP002")
        
        # Get active employees only
        employees = get_all_employees(include_inactive=False)
        assert len(employees) == 1
        assert employees[0].employee_id == "EMP001"
        
        # Get all employees including inactive
        employees = get_all_employees(include_inactive=True)
        assert len(employees) == 2


class TestAttendanceManagement:
    def test_record_check_in(self, setup_test_db, sample_employee):
        """Test recording a check-in"""
        check_in_time = datetime.now().replace(microsecond=0)  # Remove microseconds for easier comparison
        attendance = record_check_in(
            employee_id=sample_employee.employee_id,
            check_in_time=check_in_time
        )
        
        assert attendance is not None
        assert attendance["employee_id"] == sample_employee.employee_id
        assert attendance["employee_name"] == sample_employee.name
        assert attendance["check_in"] == check_in_time
        assert attendance["status"] == "Present"
    
    def test_record_check_in_nonexistent_employee(self, setup_test_db):
        """Test recording a check-in for a non-existent employee raises error"""
        with pytest.raises(ValueError):
            record_check_in(employee_id="NOTFOUND")
    
    def test_record_check_out(self, setup_test_db, sample_employee):
        """Test recording a check-out"""
        # First check in
        check_in_time = datetime.now().replace(microsecond=0) - timedelta(hours=8)
        record_check_in(
            employee_id=sample_employee.employee_id,
            check_in_time=check_in_time
        )
        
        # Then check out
        check_out_time = datetime.now().replace(microsecond=0)
        attendance = record_check_out(
            employee_id=sample_employee.employee_id,
            check_out_time=check_out_time
        )
        
        assert attendance is not None
        assert attendance["employee_id"] == sample_employee.employee_id
        assert attendance["employee_name"] == sample_employee.name
        assert attendance["check_in"] == check_in_time
        assert attendance["check_out"] == check_out_time
        assert attendance["status"] == "Present"
    
    def test_record_check_out_without_check_in(self, setup_test_db, sample_employee):
        """Test recording a check-out without a check-in raises error"""
        with pytest.raises(ValueError):
            record_check_out(employee_id=sample_employee.employee_id)
    
    def test_mark_attendance(self, setup_test_db, sample_employee):
        """Test marking attendance for an employee"""
        today = date.today()
        attendance = mark_attendance(
            employee_id=sample_employee.employee_id,
            attendance_date=today,
            status="Leave"
        )
        
        assert attendance is not None
        assert attendance["employee_id"] == sample_employee.employee_id
        assert attendance["date"] == today
        assert attendance["status"] == "Leave"
    
    def test_mark_attendance_nonexistent_employee(self, setup_test_db):
        """Test marking attendance for a non-existent employee raises error"""
        with pytest.raises(ValueError):
            mark_attendance(employee_id="NOTFOUND")
    
    def test_update_existing_attendance(self, setup_test_db, sample_employee):
        """Test updating existing attendance by marking it again"""
        today = date.today()
        
        # First mark as Present
        mark_attendance(
            employee_id=sample_employee.employee_id,
            attendance_date=today,
            status="Present"
        )
        
        # Then update to Leave
        attendance = mark_attendance(
            employee_id=sample_employee.employee_id,
            attendance_date=today,
            status="Leave"
        )
        
        assert attendance["status"] == "Leave"
    
    def test_get_attendance_history(self, setup_test_db, sample_employee_with_attendance):
        """Test getting attendance history for an employee"""
        employee = sample_employee_with_attendance
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        history = get_attendance_history(
            employee_id=employee.employee_id,
            start_date=yesterday,
            end_date=today
        )
        
        assert len(history) == 2
        
        # Check that records are for the right dates
        dates = {record["date"] for record in history}
        assert today in dates
        assert yesterday in dates
        
        # Check that records have the correct employee details
        for record in history:
            assert record["employee_id"] == employee.employee_id
            assert record["employee_name"] == employee.name
    
    def test_get_attendance_history_nonexistent_employee(self, setup_test_db):
        """Test getting attendance history for a non-existent employee raises error"""
        with pytest.raises(ValueError):
            get_attendance_history(employee_id="NOTFOUND")
    
    def test_get_attendance_report(self, setup_test_db):
        """Test getting attendance report for all employees"""
        # Create some employees
        emp1 = create_employee(
            name="Employee 1", 
            email="emp1@example.com", 
            employee_id="EMP001"
        )
        emp2 = create_employee(
            name="Employee 2", 
            email="emp2@example.com", 
            employee_id="EMP002"
        )
        emp3 = create_employee(
            name="Employee 3", 
            email="emp3@example.com", 
            employee_id="EMP003"
        )
        
        # Deactivate one employee
        deactivate_employee(emp3.employee_id)
        
        today = date.today()
        
        # Mark attendance with different statuses
        mark_attendance(employee_id=emp1.employee_id, attendance_date=today, status="Present")
        mark_attendance(employee_id=emp2.employee_id, attendance_date=today, status="Leave")
        
        # Get attendance report
        report = get_attendance_report(report_date=today, include_inactive=False)
        
        # Check report structure
        assert "present" in report
        assert "absent" in report
        assert "leave" in report
        
        # Check the employee counts
        assert len(report["present"]) == 1
        assert len(report["leave"]) == 1
        assert len(report["absent"]) == 0  # None should be absent (there are only 2 active employees)
        
        # Check that the inactive employee is not included
        all_employees = []
        for status, employees in report.items():
            all_employees.extend([e["employee_id"] for e in employees])
        
        assert emp3.employee_id not in all_employees
        
        # Get report with inactive employees
        report_with_inactive = get_attendance_report(report_date=today, include_inactive=True)
        
        # The inactive employee should be in the "absent" category
        assert len(report_with_inactive["absent"]) >= 1
        absent_ids = [e["employee_id"] for e in report_with_inactive["absent"]]
        assert emp3.employee_id in absent_ids


class TestUtilityFunctions:
    def test_calculate_hours_worked(self):
        """Test calculating hours worked from check-in and check-out times"""
        check_in = datetime.now()
        check_out = check_in + timedelta(hours=8, minutes=30)
        
        hours = _calculate_hours_worked(check_in, check_out)
        assert hours == 8.5
    
    def test_calculate_hours_worked_none(self):
        """Test calculating hours worked with missing times returns None"""
        check_in = datetime.now()
        
        # Only check-in, no check-out
        hours = _calculate_hours_worked(check_in, None)
        assert hours is None
        
        # No check-in or check-out
        hours = _calculate_hours_worked(None, None)
        assert hours is None