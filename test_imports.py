#!/usr/bin/env python3
"""
Simple test to verify all modules can be imported without configuration issues
"""
import sys
import os

def test_imports():
    try:
        # Test basic imports
        from backend.main import app
        print("✓ main.py imports successfully")
        
        # Test database imports
        from backend.database import engine, Base, get_db
        print("✓ database.py imports successfully")
        
        # Test config imports
        from backend.core.config import settings
        print("✓ config.py imports successfully")
        
        # Test model imports
        from backend.models.task import Task
        from backend.models.user import User
        from backend.models.time_session import TimeSession
        from backend.models.achievement import Achievement
        from backend.models.user_achievement import UserAchievement
        print("✓ models import successfully")
        
        # Test schema imports
        from backend.schemas.task import TaskCreate, TaskUpdate, Task
        from backend.schemas.user import UserCreate, UserUpdate, User
        from backend.schemas.time_session import TimeSessionCreate, TimeSessionUpdate, TimeSession
        from backend.schemas.achievement import AchievementCreate, AchievementUpdate, Achievement
        print("✓ schemas import successfully")
        
        # Test CRUD imports
        from backend.crud.task import create_task, get_task, get_tasks, update_task, delete_task
        from backend.crud.user import create_user, get_user, get_users
        from backend.crud.time_session import create_time_session, get_time_session, get_time_sessions, update_time_session, delete_time_session
        from backend.crud.achievement import create_achievement, get_achievement, get_achievements
        print("✓ crud imports successfully")
        
        # Test router imports
        from backend.routers.tasks import router as tasks_router
        from backend.routers.users import router as users_router
        from backend.routers.time_sessions import router as time_sessions_router
        from backend.routers.achievements import router as achievements_router
        print("✓ routers import successfully")
        
        print("\n✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
