"""
Easy API module for SQL Database Attendance System

This module provides simplified functions for common attendance system operations,
making the package easier to use without dealing with database sessions, service
instantiation, and exception handling.
"""

import os
import sys
from datetime import date, datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Union, Tuple

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import init_db, get_db, Base, engine
from src.database.models import Identity, Attendance
from src.services.identity_service import IdentityService
from src.services.attendance_service import AttendanceService


# Initialize the database if it doesn't exist
def setup_database():
    """
    Initialize the database with all required tables.
    Call this once when setting up the application.
    """
    init_db()
    return True


@contextmanager
def get_session():
    """
    Context manager for database sessions.
    Automatically handles session creation and cleanup.
    
    Usage:
    with get_session() as session:
        # use session here
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


class EmployeeData:
    """Class representing employee data for creating or retrieving identity records"""
    def __init__(self, name: str, email: str, employee_id: str, phone: str = None, is_active: bool = True):
        self.name = name
        self.email = email
        self.employee_id = employee_id
        self.phone = phone
        self.is_active = is_active
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee data to dictionary for database operations"""
        return {
            'name': self.name,
            'email': self.email,
            'employee_id': self.employee_id,
            'phone': self.phone,
            'is_active': self.is_active
        }
        
    @classmethod
    def from_identity(cls, identity: Identity):
        """Create an EmployeeData object from an Identity database model"""
        if not identity:
            return None
        return cls(
            name=identity.name,
            email=identity.email,
            employee_id=identity.employee_id,
            phone=identity.phone,
            is_active=identity.is_active
        )
    
    def __str__(self) -> str:
        return f"Employee: {self.name} ({self.employee_id})"


# ========== EMPLOYEE MANAGEMENT FUNCTIONS ==========

def create_employee(name: str, email: str, employee_id: str, phone: str = None) -> EmployeeData:
    """
    Create a new employee in the database.
    
    Args:
        name: Employee's full name
        email: Employee's email address
        employee_id: Unique employee identifier
        phone: Optional phone number
        
    Returns:
        EmployeeData object for the new employee
        
    Raises:
        ValueError: If an employee with the same email or employee_id already exists
    """
    with get_session() as session:
        identity_service = IdentityService(session)
        
        try:
            identity = identity_service.create_identity(
                name=name,
                email=email,
                employee_id=employee_id,
                phone=phone
            )
            return EmployeeData.from_identity(identity)
        except Exception as e:
            raise ValueError(f"Failed to create employee: {str(e)}")


def get_employee(employee_id: str = None, email: str = None) -> Optional[EmployeeData]:
    """
    Get an employee by employee ID or email.
    
    Args:
        employee_id: Employee's unique identifier
        email: Employee's email address
        
    Returns:
        EmployeeData object if found, None otherwise
        
    Note:
        At least one of employee_id or email must be provided
    """
    if not employee_id and not email:
        raise ValueError("Either employee_id or email must be provided")
        
    with get_session() as session:
        identity_service = IdentityService(session)
        
        identity = None
        if employee_id:
            identity = identity_service.get_identity_by_employee_id(employee_id)
        
        if not identity and email:
            identity = identity_service.get_identity_by_email(email)
            
        return EmployeeData.from_identity(identity)


def update_employee(
    employee_id: str, 
    name: str = None, 
    email: str = None, 
    phone: str = None
) -> Optional[EmployeeData]:
    """
    Update an employee's information.
    
    Args:
        employee_id: Employee's unique identifier
        name: New name (optional)
        email: New email (optional)
        phone: New phone (optional)
        
    Returns:
        Updated EmployeeData object if successful, None if employee not found
    """
    with get_session() as session:
        identity_service = IdentityService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            return None
            
        # Prepare update data
        update_data = {}
        if name:
            update_data['name'] = name
        if email:
            update_data['email'] = email
        if phone is not None:  # Allow empty string to clear phone
            update_data['phone'] = phone
            
        # Update if there's data to update
        if update_data:
            updated_identity = identity_service.update_identity(identity.id, **update_data)
            return EmployeeData.from_identity(updated_identity)
        
        return EmployeeData.from_identity(identity)


def deactivate_employee(employee_id: str) -> bool:
    """
    Deactivate an employee (soft delete).
    
    Args:
        employee_id: Employee's unique identifier
        
    Returns:
        True if successful, False if employee not found
    """
    with get_session() as session:
        identity_service = IdentityService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            return False
            
        # Deactivate the identity
        identity_service.deactivate_identity(identity.id)
        return True


def reactivate_employee(employee_id: str) -> bool:
    """
    Reactivate a previously deactivated employee.
    
    Args:
        employee_id: Employee's unique identifier
        
    Returns:
        True if successful, False if employee not found
    """
    with get_session() as session:
        identity_service = IdentityService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            return False
            
        # Reactivate the identity
        identity_service.reactivate_identity(identity.id)
        return True


def get_all_employees(include_inactive: bool = False) -> List[EmployeeData]:
    """
    Get all employees in the system.
    
    Args:
        include_inactive: Whether to include deactivated employees
        
    Returns:
        List of EmployeeData objects
    """
    with get_session() as session:
        identity_service = IdentityService(session)
        
        # Get all identities
        identities = identity_service.get_all_identities(limit=1000)
        
        # Filter out inactive identities if needed
        if not include_inactive:
            identities = [i for i in identities if i.is_active]
            
        # Convert to EmployeeData objects
        return [EmployeeData.from_identity(i) for i in identities]


# ========== ATTENDANCE MANAGEMENT FUNCTIONS ==========

def record_check_in(
    employee_id: str, 
    check_in_time: datetime = None
) -> Dict[str, Any]:
    """
    Record an employee check-in.
    
    Args:
        employee_id: Employee's unique identifier
        check_in_time: Check-in time (defaults to current time)
        
    Returns:
        Dictionary with attendance details
        
    Raises:
        ValueError: If employee not found or check-in failed
    """
    if check_in_time is None:
        check_in_time = datetime.now()
        
    attendance_date = check_in_time.date()
    
    with get_session() as session:
        identity_service = IdentityService(session)
        attendance_service = AttendanceService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            raise ValueError(f"Employee with ID {employee_id} not found")
            
        try:
            # Record check-in
            attendance = attendance_service.record_check_in(
                identity_id=identity.id,
                attendance_date=attendance_date,
                check_in_time=check_in_time
            )
            
            # Return attendance details
            return {
                'employee_id': employee_id,
                'employee_name': identity.name,
                'date': attendance.date,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'status': attendance.status
            }
        except Exception as e:
            raise ValueError(f"Failed to record check-in: {str(e)}")


def record_check_out(
    employee_id: str, 
    check_out_time: datetime = None
) -> Dict[str, Any]:
    """
    Record an employee check-out.
    
    Args:
        employee_id: Employee's unique identifier
        check_out_time: Check-out time (defaults to current time)
        
    Returns:
        Dictionary with attendance details
        
    Raises:
        ValueError: If employee not found, no check-in record, or check-out failed
    """
    if check_out_time is None:
        check_out_time = datetime.now()
        
    attendance_date = check_out_time.date()
    
    with get_session() as session:
        identity_service = IdentityService(session)
        attendance_service = AttendanceService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            raise ValueError(f"Employee with ID {employee_id} not found")
            
        try:
            # Record check-out
            attendance = attendance_service.record_check_out(
                identity_id=identity.id,
                attendance_date=attendance_date,
                check_out_time=check_out_time
            )
            
            # Return attendance details
            return {
                'employee_id': employee_id,
                'employee_name': identity.name,
                'date': attendance.date,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'status': attendance.status
            }
        except Exception as e:
            raise ValueError(f"Failed to record check-out: {str(e)}")


def get_attendance_history(
    employee_id: str, 
    start_date: date = None, 
    end_date: date = None
) -> List[Dict[str, Any]]:
    """
    Get attendance history for an employee.
    
    Args:
        employee_id: Employee's unique identifier
        start_date: Start date for the history (defaults to 30 days ago)
        end_date: End date for the history (defaults to today)
        
    Returns:
        List of attendance records
        
    Raises:
        ValueError: If employee not found
    """
    if end_date is None:
        end_date = date.today()
        
    if start_date is None:
        start_date = end_date - timedelta(days=30)
        
    with get_session() as session:
        identity_service = IdentityService(session)
        attendance_service = AttendanceService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            raise ValueError(f"Employee with ID {employee_id} not found")
            
        # Get attendance history
        attendance_records = attendance_service.get_attendance_by_date_range(
            identity_id=identity.id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to dictionaries
        return [
            {
                'employee_id': employee_id,
                'employee_name': identity.name,
                'date': record.date,
                'check_in': record.check_in,
                'check_out': record.check_out,
                'status': record.status,
                'hours_worked': _calculate_hours_worked(record.check_in, record.check_out)
            }
            for record in attendance_records
        ]


def mark_attendance(
    employee_id: str,
    attendance_date: date = None,
    status: str = "Present"
) -> Dict[str, Any]:
    """
    Mark attendance for an employee on a specific date.
    
    Args:
        employee_id: Employee's unique identifier
        attendance_date: Date for the attendance (defaults to today)
        status: Attendance status (e.g., "Present", "Absent", "Leave")
        
    Returns:
        Dictionary with attendance details
        
    Raises:
        ValueError: If employee not found or attendance marking failed
    """
    if attendance_date is None:
        attendance_date = date.today()
        
    with get_session() as session:
        identity_service = IdentityService(session)
        attendance_service = AttendanceService(session)
        
        # Get the identity by employee ID
        identity = identity_service.get_identity_by_employee_id(employee_id)
        if not identity:
            raise ValueError(f"Employee with ID {employee_id} not found")
            
        try:
            # Check if attendance record already exists for this date
            existing_records = attendance_service.get_attendance_by_date_range(
                identity_id=identity.id,
                start_date=attendance_date,
                end_date=attendance_date
            )
            
            attendance = None
            if existing_records:
                # Update existing record
                attendance = existing_records[0]
                attendance = attendance_service.update_attendance_status(
                    attendance_id=attendance.id,
                    status=status
                )
            else:
                # Create new attendance record
                attendance = attendance_service.create_attendance(
                    identity_id=identity.id,
                    attendance_date=attendance_date,
                    status=status
                )
            
            # Return attendance details
            return {
                'employee_id': employee_id,
                'employee_name': identity.name,
                'date': attendance.date,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'status': attendance.status
            }
        except Exception as e:
            raise ValueError(f"Failed to mark attendance: {str(e)}")


def get_attendance_report(
    report_date: date = None,
    include_inactive: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get attendance report for all employees on a specific date.
    
    Args:
        report_date: Date for the report (defaults to today)
        include_inactive: Whether to include deactivated employees
        
    Returns:
        Dictionary with attendance summary grouped by status
    """
    if report_date is None:
        report_date = date.today()
        
    with get_session() as session:
        identity_service = IdentityService(session)
        attendance_service = AttendanceService(session)
        
        # Get all identities
        identities = identity_service.get_all_identities(limit=1000)
        if not include_inactive:
            identities = [i for i in identities if i.is_active]
            
        # Get all attendance records for the date
        all_attendance = attendance_service.get_attendance_by_date(report_date)
        
        # Create a lookup dictionary for attendance records
        attendance_lookup = {a.identity_id: a for a in all_attendance}
        
        # Prepare report data
        report = {
            'present': [],
            'absent': [],
            'late': [],
            'leave': [],
            'other': []
        }
        
        for identity in identities:
            attendance = attendance_lookup.get(identity.id)
            
            attendance_data = {
                'employee_id': identity.employee_id,
                'employee_name': identity.name,
                'date': report_date,
                'check_in': attendance.check_in if attendance else None,
                'check_out': attendance.check_out if attendance else None,
                'status': attendance.status if attendance else "Absent",
                'hours_worked': _calculate_hours_worked(
                    attendance.check_in if attendance else None,
                    attendance.check_out if attendance else None
                )
            }
            
            status_key = attendance.status.lower() if attendance and attendance.status else "absent"
            if status_key not in report:
                status_key = "other"
                
            report[status_key].append(attendance_data)
            
        return report


# ========== UTILITY FUNCTIONS ==========

def _calculate_hours_worked(check_in: datetime, check_out: datetime) -> Optional[float]:
    """
    Calculate hours worked based on check-in and check-out times.
    
    Args:
        check_in: Check-in datetime
        check_out: Check-out datetime
        
    Returns:
        Hours worked as float, or None if either time is missing
    """
    if not check_in or not check_out:
        return None
        
    delta = check_out - check_in
    hours = delta.total_seconds() / 3600
    return round(hours, 2)