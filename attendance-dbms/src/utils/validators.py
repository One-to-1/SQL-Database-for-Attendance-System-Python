def validate_identity_data(identity_data):
    if not isinstance(identity_data, dict):
        raise ValueError("Identity data must be a dictionary.")
    
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in identity_data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(identity_data['name'], str) or not identity_data['name']:
        raise ValueError("Name must be a non-empty string.")
    
    if not isinstance(identity_data['email'], str) or "@" not in identity_data['email']:
        raise ValueError("Email must be a valid email address.")
    
    if not isinstance(identity_data['phone'], str) or not identity_data['phone'].isdigit():
        raise ValueError("Phone must be a numeric string.")

def validate_attendance_data(attendance_data):
    if not isinstance(attendance_data, dict):
        raise ValueError("Attendance data must be a dictionary.")
    
    required_fields = ['identity_id', 'date', 'status']
    for field in required_fields:
        if field not in attendance_data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(attendance_data['identity_id'], int) or attendance_data['identity_id'] <= 0:
        raise ValueError("Identity ID must be a positive integer.")
    
    if not isinstance(attendance_data['date'], str):
        raise ValueError("Date must be a string.")
    
    if attendance_data['status'] not in ['present', 'absent']:
        raise ValueError("Status must be either 'present' or 'absent'.")