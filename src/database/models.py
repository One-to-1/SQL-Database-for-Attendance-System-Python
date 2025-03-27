from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
import datetime
from .connection import Base

class Identity(Base):
    __tablename__ = "identities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    student_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship with Attendance
    attendances = relationship("Attendance", back_populates="identity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Identity {self.name} ({self.student_id})>"

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"))
    date = Column(Date, nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)  # E.g., "Present", "Absent", "Late", etc.
    
    # Relationship with Identity
    identity = relationship("Identity", back_populates="attendances")
    
    def __repr__(self):
        return f"<Attendance {self.identity_id} on {self.date}>"