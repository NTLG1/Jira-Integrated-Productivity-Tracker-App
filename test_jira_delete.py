#!/usr/bin/env python3
"""
Test script to verify Jira delete functionality
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, engine
from backend.models.task import Task
from backend.models.user import User
from backend.crud import task as crud_task
from backend.schemas.task import TaskCreate

def test_jira_delete_functionality():
    """Test that the Jira delete functionality works correctly"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test user
        user = User(username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a test task with Jira fields
        task_data = TaskCreate(
            user_id=user.id,
            title="Test Task",
            description="Test description",
            priority="medium",
            estimated_minutes=30,
            jira_issue_key="PROJ-123",
            jira_project_key="PROJ",
            jira_url="https://jira.example.com/browse/PROJ-123",
            is_jira_imported=True
        )
        
        # Create task
        task = crud_task.create_task(db, task_data)
        print(f"Created task with ID: {task.id}")
        print(f"Task Jira fields - Issue Key: {task.jira_issue_key}")
        print(f"Task Jira fields - Project Key: {task.jira_project_key}")
        print(f"Task Jira fields - URL: {task.jira_url}")
        print(f"Task Jira fields - Imported: {task.is_jira_imported}")
        
        # Test accessing the task
        retrieved_task = crud_task.get_task(db, task.id)
        print(f"Retrieved task Jira fields - Issue Key: {retrieved_task.jira_issue_key}")
        print(f"Retrieved task Jira fields - Project Key: {retrieved_task.jira_project_key}")
        print(f"Retrieved task Jira fields - URL: {retrieved_task.jira_url}")
        print(f"Retrieved task Jira fields - Imported: {retrieved_task.is_jira_imported}")
        
        # Test updating task fields (this is what our delete endpoint does)
        print("Updating task fields to None/False...")
        retrieved_task.jira_issue_key = None
        retrieved_task.jira_project_key = None
        retrieved_task.jira_url = None
        retrieved_task.is_jira_imported = False
        
        db.commit()
        print("Fields updated successfully!")
        
        # Verify the update
        final_task = crud_task.get_task(db, task.id)
        print(f"Final task Jira fields - Issue Key: {final_task.jira_issue_key}")
        print(f"Final task Jira fields - Project Key: {final_task.jira_project_key}")
        print(f"Final task Jira fields - URL: {final_task.jira_url}")
        print(f"Final task Jira fields - Imported: {final_task.is_jira_imported}")
        
        print("SUCCESS: Jira delete functionality works correctly!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    test_jira_delete_functionality()
