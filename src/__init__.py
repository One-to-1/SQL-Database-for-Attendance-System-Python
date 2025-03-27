"""
Attendance Database Management System
A Python library for managing attendance records and identities
"""

from src.database.connection import init_db  # Changed back to src.database.connection

def initialize():
    """Initialize the database by creating all tables"""
    init_db()