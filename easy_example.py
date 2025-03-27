"""
Example script demonstrating the object-oriented approach with the SQL Database Attendance System
"""

from src.api.easy_api import (
    setup_database,
    create_student,
    get_student,
    record_check_in,
    record_check_out,
    get_attendance_history,
    get_attendance_report,
    StudentData,
    mark_attendance
)
from datetime import datetime, timedelta


def main():
    print("Setting up the database...")
    setup_database()
    
    # 1. Define student objects first
    print("\n1. Creating students using StudentData class...")
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
    
    # 2. Create or retrieve students
    print("\n2. Registering students in the system...")
    student1 = register_student(first_student)
    student2 = register_student(second_student)
    
    # 3. Record attendance for first student
    print(f"\n3. Recording check-in and check-out for {student1.name}...")
    try:
        # Check in
        check_in_data = record_check_in(student_id=student1.student_id)
        print(f"  Check-in recorded at: {check_in_data['check_in'].strftime('%H:%M:%S')}")
        
        # Simulate check-out 8 hours later
        check_out_time = datetime.now() + timedelta(hours=8)
        check_out_data = record_check_out(
            student_id=student1.student_id, 
            check_out_time=check_out_time
        )
        print(f"  Check-out recorded at: {check_out_data['check_out'].strftime('%H:%M:%S')}")
        hours_worked = (check_out_data['check_out'] - check_out_data['check_in']).total_seconds() / 3600
        print(f"  Hours worked: {round(hours_worked, 2)}")
    except ValueError as e:
        print(f"  Error: {e}")
    
    # 4. Mark second student as present without check-in/check-out
    print(f"\n4. Marking attendance for {student2.name}...")
    try:
        attendance_data = mark_attendance(
            student_id=student2.student_id,
            status="Present"
        )
        print(f"  Marked status: {attendance_data['status']}")
    except ValueError as e:
        print(f"  Error: {e}")
    
    # 5. Get attendance history for first student
    print(f"\n5. Retrieving attendance history for {student1.name}...")
    try:
        history = get_attendance_history(student_id=student1.student_id)
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
    
    print("\n  Present students:")
    for student in report['present']:
        print(f"    {student['student_name']} ({student['student_id']})")
        if student['hours_worked']:
            print(f"      Hours: {student['hours_worked']}")
    
    print("\n  Absent students:")
    for student in report['absent']:
        print(f"    {student['student_name']} ({student['student_id']})")
    
    print("\nDone!")


def register_student(student_data):
    """
    Register a student in the system (create or retrieve if already exists)
    """
    try:
        # Try to create a new student
        student = create_student(
            name=student_data.name,
            email=student_data.email,
            student_id=student_data.student_id,
            phone=student_data.phone
        )
        print(f"  Created: {student}")
        return student
    except ValueError as e:
        # Student might already exist
        print(f"  Note: {str(e)}")
        # Try to retrieve the existing student
        student = get_student(student_id=student_data.student_id)
        if student:
            print(f"  Found existing: {student}")
            return student
        else:
            raise ValueError(f"Could not create or retrieve student {student_data.student_id}")


if __name__ == "__main__":
    main()