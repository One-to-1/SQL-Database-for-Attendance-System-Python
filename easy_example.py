"""
Example script demonstrating the object-oriented approach with the SQL Database Attendance System
"""

from src.api.easy_api import (
    setup_database,
    create_employee,
    get_employee,
    record_check_in,
    record_check_out,
    get_attendance_history,
    get_attendance_report,
    EmployeeData,
    mark_attendance
)
from datetime import datetime, timedelta


def main():
    print("Setting up the database...")
    setup_database()
    
    # 1. Define employee objects first
    print("\n1. Creating employees using EmployeeData class...")
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
    
    # 2. Create or retrieve employees
    print("\n2. Registering employees in the system...")
    employee1 = register_employee(first_employee)
    employee2 = register_employee(second_employee)
    
    # 3. Record attendance for first employee
    print(f"\n3. Recording check-in and check-out for {employee1.name}...")
    try:
        # Check in
        check_in_data = record_check_in(employee_id=employee1.employee_id)
        print(f"  Check-in recorded at: {check_in_data['check_in'].strftime('%H:%M:%S')}")
        
        # Simulate check-out 8 hours later
        check_out_time = datetime.now() + timedelta(hours=8)
        check_out_data = record_check_out(
            employee_id=employee1.employee_id, 
            check_out_time=check_out_time
        )
        print(f"  Check-out recorded at: {check_out_data['check_out'].strftime('%H:%M:%S')}")
        hours_worked = (check_out_data['check_out'] - check_out_data['check_in']).total_seconds() / 3600
        print(f"  Hours worked: {round(hours_worked, 2)}")
    except ValueError as e:
        print(f"  Error: {e}")
    
    # 4. Mark second employee as present without check-in/check-out
    print(f"\n4. Marking attendance for {employee2.name}...")
    try:
        attendance_data = mark_attendance(
            employee_id=employee2.employee_id,
            status="Present"
        )
        print(f"  Marked status: {attendance_data['status']}")
    except ValueError as e:
        print(f"  Error: {e}")
    
    # 5. Get attendance history for first employee
    print(f"\n5. Retrieving attendance history for {employee1.name}...")
    try:
        history = get_attendance_history(employee_id=employee1.employee_id)
        print(f"  Found {len(history)} attendance records:")
        for record in history:
            print(f"  Date: {record['date']}, Status: {record['status']}")
            if record['check_in']:
                print(f"    Check-in: {record['check_in'].strftime('%H:%M:%S')}")
            if record['check_out']:
                print(f"    Check-out: {record['check_out'].strftime('%H:%M:%S')}")
            if record['hours_worked']:
                print(f"    Hours worked: {record['hours_worked']}")
    except ValueError as e:
        print(f"  Error: {e}")
    
    # 6. Generate attendance report
    print("\n6. Generating attendance report for today...")
    report = get_attendance_report()
    
    print("\n  Present employees:")
    for emp in report['present']:
        print(f"    {emp['employee_name']} ({emp['employee_id']})")
        if emp['hours_worked']:
            print(f"      Hours: {emp['hours_worked']}")
    
    print("\n  Absent employees:")
    for emp in report['absent']:
        print(f"    {emp['employee_name']} ({emp['employee_id']})")
    
    print("\nDone!")


def register_employee(employee_data):
    """
    Register an employee in the system (create or retrieve if already exists)
    """
    try:
        # Try to create a new employee
        employee = create_employee(
            name=employee_data.name,
            email=employee_data.email,
            employee_id=employee_data.employee_id,
            phone=employee_data.phone
        )
        print(f"  Created: {employee}")
        return employee
    except ValueError as e:
        # Employee might already exist
        print(f"  Note: {str(e)}")
        # Try to retrieve the existing employee
        employee = get_employee(employee_id=employee_data.employee_id)
        if employee:
            print(f"  Found existing: {employee}")
            return employee
        else:
            raise ValueError(f"Could not create or retrieve employee {employee_data.employee_id}")


if __name__ == "__main__":
    main()