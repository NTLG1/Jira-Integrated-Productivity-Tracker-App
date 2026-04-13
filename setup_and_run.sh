#!/bin/bash

echo "Setting up the productivity tracker backend..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create database tables
echo "Creating database tables..."
python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, engine
from backend.core.config import settings

# Create all tables
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

echo "Starting the application..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
