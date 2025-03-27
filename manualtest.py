import os
import sys
from datetime import date, datetime

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the necessary modules
from src.database.connection import init_db, get_db, Base, engine
from src.database.models import Identity, Attendance
from src.services.identity_service import IdentityService
from src.services.attendance_service import AttendanceService

class EmployeeData:
    """Class representing employee data for creating or retrieving identity records"""
    def __init__(self, name, email, employee_id, phone=None, is_active=True):
        self.name = name
        self.email = email
        self.employee_id = employee_id
        self.phone = phone
        self.is_active = is_active
        
    def to_dict(self):
        """Convert employee data to dictionary for database operations"""
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

def main():
    print("Initializing database...")
    # Initialize the database with all tables
    Base.metadata.create_all(bind=engine)
    
    # Get a database session
    db = next(get_db())
    
    # Create services
    identity_service = IdentityService(db)
    attendance_service = AttendanceService(db)
    
    # Create a test employee data object
    test_employee = EmployeeData(
        name="Test Employee",
        email="test@example.com",
        employee_id="TEST001",
        phone="555-1234"
    )
    
    # Create a test identity
    print("Creating test identity...")
    try:
        # Use the object-oriented approach to create identity
        employee = identity_service.create_identity(**test_employee.to_dict())
        print(f"Created employee: {employee.name} (ID: {employee.id})")
    except Exception as e:
        print(f"Error creating identity: {e}")
        # Check if identity already exists
        employee = identity_service.get_identity_by_employee_id(test_employee.employee_id)
        if employee:
            # Convert the database model back to our object representation
            existing_employee = EmployeeData.from_identity(employee)
            print(f"Found existing employee: {existing_employee.name} (ID: {employee.id})")
    
    if employee:
        # Record attendance for today
        print("Recording attendance...")
        try:
            today = date.today()
            attendance = attendance_service.record_check_in(
                identity_id=employee.id,
                attendance_date=today,
                check_in_time=datetime.now()
            )
            print(f"Recorded check-in for {employee.name} at {attendance.check_in}")
        except Exception as e:
            print(f"Error recording attendance: {e}")
        
        # Get attendance history
        print("\nAttendance history:")
        try:
            history = attendance_service.get_attendance_by_identity(employee.id)
            for record in history:
                print(f"Date: {record.date}, Status: {record.status}")
                if record.check_in:
                    print(f"  Check-in: {record.check_in}")
                if record.check_out:
                    print(f"  Check-out: {record.check_out}")
        except Exception as e:
            print(f"Error retrieving attendance history: {e}")

if __name__ == "__main__":
    main()