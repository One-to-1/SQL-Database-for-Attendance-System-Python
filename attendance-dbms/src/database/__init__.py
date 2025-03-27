"""
Database module for the Attendance Database Management System
"""

from src.database.connection import Base, engine, get_db, init_db
from src.database.models import Identity, Attendance