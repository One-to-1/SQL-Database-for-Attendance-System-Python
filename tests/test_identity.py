import pytest
import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.database.connection import Base
from src.database.models import Identity
# Direct import from file instead of through package
from src.services.identity_service import IdentityService

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
def sample_identity(identity_service):
    identity = identity_service.create_identity(
        name="John Doe",
        email="john.doe@example.com",
        student_id="EMP001",
        phone="555-1234"
    )
    return identity

def test_create_identity(identity_service):
    identity = identity_service.create_identity(
        name="Jane Doe",
        email="jane.doe@example.com",
        student_id="EMP002",
        phone="555-5678"
    )
    
    assert identity.id is not None
    assert identity.name == "Jane Doe"
    assert identity.email == "jane.doe@example.com"
    assert identity.student_id == "EMP002"
    assert identity.phone == "555-5678"
    assert identity.is_active == True

def test_get_identity_by_id(identity_service, sample_identity):
    identity = identity_service.get_identity_by_id(sample_identity.id)
    
    assert identity is not None
    assert identity.id == sample_identity.id
    assert identity.name == sample_identity.name
    assert identity.email == sample_identity.email

def test_get_identity_by_email(identity_service, sample_identity):
    identity = identity_service.get_identity_by_email(sample_identity.email)
    
    assert identity is not None
    assert identity.id == sample_identity.id
    assert identity.email == sample_identity.email

def test_get_identity_by_student_id(identity_service, sample_identity):
    identity = identity_service.get_identity_by_student_id(sample_identity.student_id)
    
    assert identity is not None
    assert identity.id == sample_identity.id
    assert identity.student_id == sample_identity.student_id

def test_update_identity(identity_service, sample_identity):
    updated = identity_service.update_identity(
        sample_identity.id,
        name="John Updated",
        phone="555-9999"
    )
    
    assert updated.name == "John Updated"
    assert updated.phone == "555-9999"
    # Email should remain unchanged
    assert updated.email == sample_identity.email

def test_deactivate_identity(identity_service, sample_identity):
    deactivated = identity_service.deactivate_identity(sample_identity.id)
    
    assert deactivated.is_active == False
    assert deactivated.id == sample_identity.id

def test_reactivate_identity(identity_service, sample_identity):
    # First deactivate
    deactivated = identity_service.deactivate_identity(sample_identity.id)
    assert deactivated.is_active == False
    
    # Then reactivate
    reactivated = identity_service.reactivate_identity(sample_identity.id)
    assert reactivated.is_active == True

def test_delete_identity(identity_service, sample_identity):
    # First verify it exists
    identity = identity_service.get_identity_by_id(sample_identity.id)
    assert identity is not None
    
    # Delete it
    identity_service.delete_identity(sample_identity.id)
    
    # Verify it's gone
    identity = identity_service.get_identity_by_id(sample_identity.id)
    assert identity is None

def test_duplicate_email_raises_error(identity_service, sample_identity):
    with pytest.raises(ValueError):
        identity_service.create_identity(
            name="Another Person",
            email=sample_identity.email,  # Same email as existing identity
            student_id="EMP003",
            phone="555-0000"
        )