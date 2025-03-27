def validate_identity(identity):
    if not isinstance(identity, dict):
        raise ValueError("Identity must be a dictionary.")
    
    required_fields = ['id', 'name', 'email']
    for field in required_fields:
        if field not in identity:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(identity['id'], int) or identity['id'] <= 0:
        raise ValueError("Identity ID must be a positive integer.")
    
    if not isinstance(identity['name'], str) or not identity['name']:
        raise ValueError("Identity name must be a non-empty string.")
    
    if not isinstance(identity['email'], str) or '@' not in identity['email']:
        raise ValueError("Identity email must be a valid email address.")

def validate_attendance(attendance):
    if not isinstance(attendance, dict):
        raise ValueError("Attendance must be a dictionary.")
    
    required_fields = ['identity_id', 'date', 'status']
    for field in required_fields:
        if field not in attendance:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(attendance['identity_id'], int) or attendance['identity_id'] <= 0:
        raise ValueError("Identity ID must be a positive integer.")
    
    if not isinstance(attendance['date'], str) or not attendance['date']:
        raise ValueError("Attendance date must be a non-empty string.")
    
    if attendance['status'] not in ['present', 'absent']:
        raise ValueError("Attendance status must be either 'present' or 'absent'.")