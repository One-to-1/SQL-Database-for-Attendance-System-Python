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
    
    def get_identity_by_employee_id(self, employee_id: str):
        """
        Retrieve an identity by its employee ID
        """
        return self.db.query(Identity).filter(Identity.employee_id == employee_id).first()
    
    def get_identity_by_email(self, email: str):
        """
        Retrieve an identity by email
        """
        return self.db.query(Identity).filter(Identity.email == email).first()
    
    def create_identity(self, name: str, email: str, employee_id: str, phone: str = None):
        """
        Create a new identity in the database
        """
        try:
            identity = Identity(
                name=name,
                email=email,
                phone=phone,
                employee_id=employee_id,
                created_at=datetime.utcnow(),
                is_active=True
            )
            self.db.add(identity)
            self.db.commit()
            self.db.refresh(identity)
            return identity
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Identity with this email or employee ID already exists")
    
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