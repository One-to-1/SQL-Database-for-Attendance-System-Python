import pytest
import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.database.connection import Base
from src.database.models import Identity, Attendance
# Direct import from file instead of through package
from src.services.identity_service import IdentityService
from src.services.attendance_service import AttendanceService

# Set up an in-memory SQLite database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

@pytest.fixture
def identity_service(db_session):
    return IdentityService(db_session)

@pytest.fixture
def attendance_service(db_session):
    return AttendanceService(db_session)

@pytest.fixture
def sample_identity(identity_service):
    identity = identity_service.create_identity(
        name="John Doe",
        email="john.doe@example.com",
        employee_id="EMP001",
        phone="555-1234"
    )
    return identity

@pytest.fixture
def sample_attendance(attendance_service, sample_identity):
    today = date.today()
    attendance = attendance_service.create_attendance(
        identity_id=sample_identity.id,
        attendance_date=today,
        status="Present"
    )
    return attendance

def test_create_attendance(attendance_service, sample_identity):
    today = date.today()
    attendance = attendance_service.create_attendance(
        identity_id=sample_identity.id,
        attendance_date=today,
        status="Present"
    )
    
    assert attendance.id is not None
    assert attendance.identity_id == sample_identity.id
    assert attendance.date == today
    assert attendance.status == "Present"

def test_duplicate_attendance_raises_error(attendance_service, sample_attendance):
    today = date.today()
    with pytest.raises(ValueError):
        attendance_service.create_attendance(
            identity_id=sample_attendance.identity_id,
            attendance_date=today,
            status="Absent"  # Different status, but same date and identity
        )

def test_get_attendance_by_id(attendance_service, sample_attendance):
    attendance = attendance_service.get_attendance_by_id(sample_attendance.id)
    
    assert attendance is not None
    assert attendance.id == sample_attendance.id
    assert attendance.identity_id == sample_attendance.identity_id

def test_get_attendance_by_date(attendance_service, sample_attendance):
    today = date.today()
    attendances = attendance_service.get_attendance_by_date(today)
    
    assert len(attendances) == 1
    assert attendances[0].id == sample_attendance.id
    assert attendances[0].date == today

def test_get_attendance_by_identity(attendance_service, sample_identity, sample_attendance):
    attendances = attendance_service.get_attendance_by_identity(sample_identity.id)
    
    assert len(attendances) == 1
    assert attendances[0].id == sample_attendance.id
    assert attendances[0].identity_id == sample_identity.id

def test_record_check_in(attendance_service, sample_identity):
    today = date.today()
    check_in_time = datetime.now()
    
    attendance = attendance_service.record_check_in(
        identity_id=sample_identity.id,
        attendance_date=today,
        check_in_time=check_in_time
    )
    
    assert attendance is not None
    assert attendance.identity_id == sample_identity.id
    assert attendance.date == today
    assert attendance.check_in is not None
    assert attendance.check_in == check_in_time
    assert attendance.status == "Present"

def test_record_check_out(attendance_service, sample_identity):
    today = date.today()
    check_in_time = datetime.now()
    
    # First check in
    attendance = attendance_service.record_check_in(
        identity_id=sample_identity.id,
        attendance_date=today,
        check_in_time=check_in_time
    )
    
    # Then check out
    check_out_time = check_in_time + timedelta(hours=8)
    attendance = attendance_service.record_check_out(
        identity_id=sample_identity.id,
        attendance_date=today,
        check_out_time=check_out_time
    )
    
    assert attendance is not None
    assert attendance.check_out is not None
    assert attendance.check_out == check_out_time

def test_update_attendance_status(attendance_service, sample_attendance):
    attendance = attendance_service.update_attendance_status(
        attendance_id=sample_attendance.id,
        status="Absent"
    )
    
    assert attendance is not None
    assert attendance.status == "Absent"

def test_delete_attendance(attendance_service, sample_attendance):
    # First verify it exists
    attendance = attendance_service.get_attendance_by_id(sample_attendance.id)
    assert attendance is not None
    
    # Delete it
    attendance_service.delete_attendance(sample_attendance.id)
    
    # Verify it's gone
    attendance = attendance_service.get_attendance_by_id(sample_attendance.id)
    assert attendance is None

def test_get_attendance_by_date_range(attendance_service, sample_identity):
    # Create attendance records for multiple dates
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    attendance_service.create_attendance(
        identity_id=sample_identity.id,
        attendance_date=yesterday,
        status="Present"
    )
    
    attendance_service.create_attendance(
        identity_id=sample_identity.id,
        attendance_date=today,
        status="Present"
    )
    
    attendance_service.create_attendance(
        identity_id=sample_identity.id,
        attendance_date=tomorrow,
        status="Present"
    )
    
    # Query for date range
    attendances = attendance_service.get_attendance_by_date_range(
        identity_id=sample_identity.id,
        start_date=yesterday,
        end_date=today
    )
    
    assert len(attendances) == 2