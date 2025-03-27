from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.models import Identity

class IdentityService:
    """
    Service class for managing identities in the database
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def get_all_identities(self, skip: int = 0, limit: int = 100):
        """
        Retrieve all identities with pagination
        """
        return self.db.query(Identity).offset(skip).limit(limit).all()
    
    def get_identity_by_id(self, identity_id: int):
        """
        Retrieve an identity by its ID
        """
        return self.db.query(Identity).filter(Identity.id == identity_id).first()
    
    def get_identity_by_student_id(self, student_id: str):
        """
        Retrieve an identity by its student ID
        """
        return self.db.query(Identity).filter(Identity.student_id == student_id).first()
    
    def get_identity_by_email(self, email: str):
        """
        Retrieve an identity by email
        """
        return self.db.query(Identity).filter(Identity.email == email).first()
    
    def create_identity(self, name: str, email: str, student_id: str, phone: str = None, is_active: bool = True):
        """
        Create a new identity in the database
        
        Can be called with individual parameters or by unpacking a StudentData object:
        service.create_identity(**student_data.to_dict())
        """
        try:
            identity = Identity(
                name=name,
                email=email,
                phone=phone,
                student_id=student_id,
                created_at=datetime.utcnow(),
                is_active=is_active
            )
            self.db.add(identity)
            self.db.commit()
            self.db.refresh(identity)
            return identity
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Identity with this email or student ID already exists")
    
    def create_identity_from_object(self, student_data):
        """
        Create a new identity from a student data object
        
        student_data should have attributes: name, email, student_id, and optionally phone and is_active
        """
        try:
            # Extract attributes from the student data object
            if hasattr(student_data, 'to_dict'):
                # If the object has a to_dict method, use it
                data_dict = student_data.to_dict()
                return self.create_identity(**data_dict)
            else:
                # Otherwise, extract attributes directly
                return self.create_identity(
                    name=getattr(student_data, 'name', None),
                    email=getattr(student_data, 'email', None),
                    student_id=getattr(student_data, 'student_id', None),
                    phone=getattr(student_data, 'phone', None),
                    is_active=getattr(student_data, 'is_active', True)
                )
        except AttributeError as e:
            raise ValueError(f"Invalid student data object: {e}")
    
    def update_identity(self, identity_id: int, **kwargs):
        """
        Update an identity with the provided fields
        """
        identity = self.get_identity_by_id(identity_id)
        if not identity:
            raise ValueError(f"Identity with ID {identity_id} does not exist")
            
        for key, value in kwargs.items():
            if hasattr(identity, key):
                setattr(identity, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(identity)
            return identity
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Update failed due to constraint violation")
    
    def update_identity_from_object(self, identity_id: int, student_data):
        """
        Update an identity using a student data object
        
        student_data should have attributes representing the fields to update
        """
        if hasattr(student_data, 'to_dict'):
            # If the object has a to_dict method, use it
            data_dict = student_data.to_dict()
            return self.update_identity(identity_id, **data_dict)
        else:
            # Extract all non-None attributes from the student data object
            update_dict = {}
            for attr in ['name', 'email', 'student_id', 'phone', 'is_active']:
                if hasattr(student_data, attr):
                    value = getattr(student_data, attr)
                    if value is not None:
                        update_dict[attr] = value
            
            return self.update_identity(identity_id, **update_dict)
    
    def deactivate_identity(self, identity_id: int):
        """
        Deactivate an identity (soft delete)
        """
        return self.update_identity(identity_id, is_active=False)
    
    def reactivate_identity(self, identity_id: int):
        """
        Reactivate a previously deactivated identity
        """
        return self.update_identity(identity_id, is_active=True)
    
    def delete_identity(self, identity_id: int):
        """
        Hard delete an identity from the database
        """
        identity = self.get_identity_by_id(identity_id)
        if not identity:
            raise ValueError(f"Identity with ID {identity_id} does not exist")
        
        self.db.delete(identity)
        self.db.commit()
        return True