import os
import sys
from datetime import date, datetime

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the necessary modules
from src.database.connection import init_db, get_db, Base, engine
from src.services.identity_service import IdentityService
from src.services.attendance_service import AttendanceService

def main():
    print("Initializing database...")
    # Initialize the database with all tables
    Base.metadata.create_all(bind=engine)
    
    # Get a database session
    db = next(get_db())
    
    # Create services
    identity_service = IdentityService(db)
    attendance_service = AttendanceService(db)
    
    # Create a test identity
    print("Creating test identity...")
    try:
        employee = identity_service.create_identity(
            name="Test Employee",
            email="test@example.com",
            employee_id="TEST001",
            phone="555-1234"
        )
        print(f"Created employee: {employee.name} (ID: {employee.id})")
    except Exception as e:
        print(f"Error creating identity: {e}")
        # Check if identity already exists
        employee = identity_service.get_identity_by_employee_id("TEST001")
        if employee:
            print(f"Found existing employee: {employee.name} (ID: {employee.id})")
    
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