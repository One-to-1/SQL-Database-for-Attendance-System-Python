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
    setup_database, get_session, StudentData,
    create_student, get_student, update_student,
    deactivate_student, reactivate_student, get_all_students,
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
def sample_student(setup_test_db):
    """Create a sample student for testing"""
    student = create_student(
        name="John Doe",
        email="john.doe@example.com",
        student_id="EMP001",
        phone="555-1234"
    )
    return student


@pytest.fixture
def sample_student_with_attendance(setup_test_db, sample_student):
    """Create a sample student with attendance records"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Create attendance for today and yesterday
    mark_attendance(
        student_id=sample_student.student_id,
        attendance_date=yesterday,
        status="Present"
    )
    
    mark_attendance(
        student_id=sample_student.student_id,
        attendance_date=today,
        status="Present"
    )
    
    return sample_student


class TestDatabaseSetup:
    def test_setup_database(self, setup_test_db):
        """Test that database setup works correctly"""
        result = setup_database()
        assert result is True


class TestStudentDataClass:
    def test_student_data_init(self):
        """Test StudentData initialization"""
        student = StudentData(
            name="Test User",
            email="test@example.com",
            student_id="EMP123",
            phone="555-5555"
        )
        
        assert student.name == "Test User"
        assert student.email == "test@example.com"
        assert student.student_id == "EMP123"
        assert student.phone == "555-5555"
        assert student.is_active is True
    
    def test_to_dict(self):
        """Test StudentData to_dict method"""
        student = StudentData(
            name="Test User",
            email="test@example.com",
            student_id="EMP123",
            phone="555-5555"
        )
        
        data_dict = student.to_dict()
        assert data_dict["name"] == "Test User"
        assert data_dict["email"] == "test@example.com"
        assert data_dict["student_id"] == "EMP123"
        assert data_dict["phone"] == "555-5555"
        assert data_dict["is_active"] is True
    
    def test_str_representation(self):
        """Test StudentData string representation"""
        student = StudentData(
            name="Test User",
            email="test@example.com",
            student_id="EMP123"
        )
        
        assert str(student) == "Student: Test User (EMP123)"


class TestStudentManagement:
    def test_create_student(self, setup_test_db):
        """Test creating a new student"""
        student = create_student(
            name="Jane Doe",
            email="jane.doe@example.com",
            student_id="EMP002",
            phone="555-5678"
        )
        
        assert student.name == "Jane Doe"
        assert student.email == "jane.doe@example.com"
        assert student.student_id == "EMP002"
        assert student.phone == "555-5678"
        assert student.is_active is True
    
    def test_create_duplicate_student(self, setup_test_db, sample_student):
        """Test creating a student with duplicate email raises error"""
        with pytest.raises(ValueError):
            create_student(
                name="Another Person",
                email=sample_student.email,  # Same email as existing student
                student_id="EMP003",
                phone="555-0000"
            )
    
    def test_get_student_by_id(self, setup_test_db, sample_student):
        """Test getting a student by ID"""
        student = get_student(student_id=sample_student.student_id)
        
        assert student is not None
        assert student.name == sample_student.name
        assert student.email == sample_student.email
        assert student.student_id == sample_student.student_id
    
    def test_get_student_by_email(self, setup_test_db, sample_student):
        """Test getting a student by email"""
        student = get_student(email=sample_student.email)
        
        assert student is not None
        assert student.name == sample_student.name
        assert student.email == sample_student.email
        assert student.student_id == sample_student.student_id
    
    def test_get_nonexistent_student(self, setup_test_db):
        """Test getting a non-existent student returns None"""
        student = get_student(student_id="NOTFOUND")
        assert student is None
        
        student = get_student(email="notfound@example.com")
        assert student is None
    
    def test_get_student_with_no_params(self, setup_test_db):
        """Test getting a student with no parameters raises error"""
        with pytest.raises(ValueError):
            get_student()
    
    def test_update_student(self, setup_test_db, sample_student):
        """Test updating a student's details"""
        updated = update_student(
            student_id=sample_student.student_id,
            name="John Updated",
            email="john.updated@example.com",
            phone="555-9999"
        )
        
        assert updated is not None
        assert updated.name == "John Updated"
        assert updated.email == "john.updated@example.com"
        assert updated.phone == "555-9999"
        assert updated.student_id == sample_student.student_id
    
    def test_update_nonexistent_student(self, setup_test_db):
        """Test updating a non-existent student returns None"""
        updated = update_student(
            student_id="NOTFOUND",
            name="Nobody"
        )
        assert updated is None
    
    def test_deactivate_student(self, setup_test_db, sample_student):
        """Test deactivating a student"""
        result = deactivate_student(sample_student.student_id)
        assert result is True
        
        # Verify the student is deactivated
        student = get_student(student_id=sample_student.student_id)
        assert student.is_active is False
    
    def test_deactivate_nonexistent_student(self, setup_test_db):
        """Test deactivating a non-existent student returns False"""
        result = deactivate_student("NOTFOUND")
        assert result is False
    
    def test_reactivate_student(self, setup_test_db, sample_student):
        """Test reactivating a student"""
        # First deactivate
        deactivate_student(sample_student.student_id)
        
        # Then reactivate
        result = reactivate_student(sample_student.student_id)
        assert result is True
        
        # Verify the student is reactivated
        student = get_student(student_id=sample_student.student_id)
        assert student.is_active is True
    
    def test_reactivate_nonexistent_student(self, setup_test_db):
        """Test reactivating a non-existent student returns False"""
        result = reactivate_student("NOTFOUND")
        assert result is False
    
    def test_get_all_students(self, setup_test_db):
        """Test getting all students"""
        # Create some students
        create_student(
            name="Student 1",
            email="student1@example.com",
            student_id="EMP001"
        )
        create_student(
            name="Student 2",
            email="student2@example.com",
            student_id="EMP002"
        )
        
        # Deactivate one student
        deactivate_student("EMP002")
        
        # Get active students only
        students = get_all_students(include_inactive=False)
        assert len(students) == 1
        assert students[0].student_id == "EMP001"
        
        # Get all students including inactive
        students = get_all_students(include_inactive=True)
        assert len(students) == 2


class TestAttendanceManagement:
    def test_record_check_in(self, setup_test_db, sample_student):
        """Test recording a check-in"""
        check_in_time = datetime.now().replace(microsecond=0)  # Remove microseconds for easier comparison
        attendance = record_check_in(
            student_id=sample_student.student_id,
            check_in_time=check_in_time
        )
        
        assert attendance is not None
        assert attendance["student_id"] == sample_student.student_id
        assert attendance["student_name"] == sample_student.name
        assert attendance["check_in"] == check_in_time
        assert attendance["status"] == "Present"
    
    def test_record_check_in_nonexistent_student(self, setup_test_db):
        """Test recording a check-in for a non-existent student raises error"""
        with pytest.raises(ValueError):
            record_check_in(student_id="NOTFOUND")
    
    def test_record_check_out(self, setup_test_db, sample_student):
        """Test recording a check-out"""
        # First check in
        check_in_time = datetime.now().replace(microsecond=0) - timedelta(hours=8)
        record_check_in(
            student_id=sample_student.student_id,
            check_in_time=check_in_time
        )
        
        # Then check out
        check_out_time = datetime.now().replace(microsecond=0)
        attendance = record_check_out(
            student_id=sample_student.student_id,
            check_out_time=check_out_time
        )
        
        assert attendance is not None
        assert attendance["student_id"] == sample_student.student_id
        assert attendance["student_name"] == sample_student.name
        assert attendance["check_in"] == check_in_time
        assert attendance["check_out"] == check_out_time
        assert attendance["status"] == "Present"
    
    def test_record_check_out_without_check_in(self, setup_test_db, sample_student):
        """Test recording a check-out without a check-in raises error"""
        with pytest.raises(ValueError):
            record_check_out(student_id=sample_student.student_id)
    
    def test_mark_attendance(self, setup_test_db, sample_student):
        """Test marking attendance for a student"""
        today = date.today()
        attendance = mark_attendance(
            student_id=sample_student.student_id,
            attendance_date=today,
            status="Leave"
        )
        
        assert attendance is not None
        assert attendance["student_id"] == sample_student.student_id
        assert attendance["date"] == today
        assert attendance["status"] == "Leave"
    
    def test_mark_attendance_nonexistent_student(self, setup_test_db):
        """Test marking attendance for a non-existent student raises error"""
        with pytest.raises(ValueError):
            mark_attendance(student_id="NOTFOUND")
    
    def test_update_existing_attendance(self, setup_test_db, sample_student):
        """Test updating existing attendance by marking it again"""
        today = date.today()
        
        # First mark as Present
        mark_attendance(
            student_id=sample_student.student_id,
            attendance_date=today,
            status="Present"
        )
        
        # Then update to Leave
        attendance = mark_attendance(
            student_id=sample_student.student_id,
            attendance_date=today,
            status="Leave"
        )
        
        assert attendance["status"] == "Leave"
    
    def test_get_attendance_history(self, setup_test_db, sample_student_with_attendance):
        """Test getting attendance history for a student"""
        student = sample_student_with_attendance
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        history = get_attendance_history(
            student_id=student.student_id,
            start_date=yesterday,
            end_date=today
        )
        
        assert len(history) == 2
        
        # Check that records are for the right dates
        dates = {record["date"] for record in history}
        assert today in dates
        assert yesterday in dates
        
        # Check that records have the correct student details
        for record in history:
            assert record["student_id"] == student.student_id
            assert record["student_name"] == student.name
    
    def test_get_attendance_history_nonexistent_student(self, setup_test_db):
        """Test getting attendance history for a non-existent student raises error"""
        with pytest.raises(ValueError):
            get_attendance_history(student_id="NOTFOUND")
    
    def test_get_attendance_report(self, setup_test_db):
        """Test getting attendance report for all students"""
        # Create some students
        student1 = create_student(
            name="Student 1", 
            email="student1@example.com", 
            student_id="EMP001"
        )
        student2 = create_student(
            name="Student 2", 
            email="student2@example.com", 
            student_id="EMP002"
        )
        student3 = create_student(
            name="Student 3", 
            email="student3@example.com", 
            student_id="EMP003"
        )
        
        # Deactivate one student
        deactivate_student(student3.student_id)
        
        today = date.today()
        
        # Mark attendance with different statuses
        mark_attendance(student_id=student1.student_id, attendance_date=today, status="Present")
        mark_attendance(student_id=student2.student_id, attendance_date=today, status="Leave")
        
        # Get attendance report
        report = get_attendance_report(report_date=today, include_inactive=False)
        
        # Check report structure
        assert "present" in report
        assert "absent" in report
        assert "leave" in report
        
        # Check the student counts
        assert len(report["present"]) == 1
        assert len(report["leave"]) == 1
        assert len(report["absent"]) == 0  # None should be absent (there are only 2 active students)
        
        # Check that the inactive student is not included
        all_students = []
        for status, students in report.items():
            all_students.extend([s["student_id"] for s in students])
        
        assert student3.student_id not in all_students
        
        # Get report with inactive students
        report_with_inactive = get_attendance_report(report_date=today, include_inactive=True)
        
        # The inactive student should be in the "absent" category
        assert len(report_with_inactive["absent"]) >= 1
        absent_ids = [s["student_id"] for s in report_with_inactive["absent"]]
        assert student3.student_id in absent_ids


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