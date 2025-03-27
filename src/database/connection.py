from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Function to get a database session
    Returns a SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables
    """
    Base.metadata.create_all(bind=engine)

class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None

    def connect(self):
        # Logic to establish a database connection
        # For example, using SQLAlchemy or another database library
        pass

    def disconnect(self):
        # Logic to close the database connection
        pass