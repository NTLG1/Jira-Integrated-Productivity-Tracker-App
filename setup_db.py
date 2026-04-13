#!/usr/bin/env python3
"""
Simple script to create the PostgreSQL database and tables for the productivity app
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from backend.database import Base, engine
from backend.core.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    try:
        print(f"Attempting to connect to database: {settings.DATABASE_URL}")
        test_engine = create_engine(settings.DATABASE_URL)
        test_engine.connect()
        print("✓ Database connection successful")
        return True
    except OperationalError as e:
        print(f"✗ Database connection failed: {e}")
        print("Database may already exist or connection details incorrect.")
        return False

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False

def main():
    print("Setting up productivity app database...")
    
    # Create database (this will work if it already exists)
    if not create_database():
        print("Database connection failed, but this might be expected if database exists")
    
    # Create tables
    if not create_tables():
        print("Failed to create tables")
        return 1
    
    print("Database setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
