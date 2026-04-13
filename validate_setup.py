"""
Validation script to verify the productivity tracker backend setup
"""
import os
import sys

def validate_directories():
    """Validate that all required directories exist"""
    required_dirs = [
        'backend',
        'backend/models',
        'backend/schemas',
        'backend/crud',
        'backend/routers',
        'backend/core'
    ]
    
    print("Validating directory structure...")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory} exists")
        else:
            print(f"✗ {directory} missing")
            return False
    return True

def validate_files():
    """Validate that all required files exist"""
    required_files = [
        # Core files
        'backend/main.py',
        'backend/database.py',
        'backend/core/config.py',
        'backend/requirements.txt',
        '.env',
        
        # Models
        'backend/models/task.py',
        'backend/models/user.py',
        'backend/models/time_session.py',
        'backend/models/achievement.py',
        'backend/models/user_achievement.py',
        
        # Schemas
        'backend/schemas/task.py',
        'backend/schemas/user.py',
        'backend/schemas/time_session.py',
        'backend/schemas/achievement.py',
        
        # CRUD
        'backend/crud/task.py',
        'backend/crud/user.py',
        'backend/crud/time_session.py',
        'backend/crud/achievement.py',
        
        # Routers
        'backend/routers/tasks.py',
        'backend/routers/users.py',
        'backend/routers/time_sessions.py',
        'backend/routers/achievements.py',
    ]
    
    print("\nValidating files...")
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_good = False
    
    return all_good

def validate_requirements():
    """Validate requirements file content"""
    print("\nValidating requirements...")
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = ['fastapi', 'sqlalchemy', 'pydantic', 'uvicorn']
            for package in required_packages:
                if package in content:
                    print(f"✓ {package} found in requirements")
                else:
                    print(f"✗ {package} missing from requirements")
                    return False
            return True
    except Exception as e:
        print(f"✗ Error reading requirements: {e}")
        return False

def main():
    """Main validation function"""
    print("=== Productivity Tracker Backend Setup Validation ===")
    
    success = True
    success &= validate_directories()
    success &= validate_files()
    success &= validate_requirements()
    
    print("\n=== Validation Complete ===")
    if success:
        print("✓ All checks passed! Backend setup is complete.")
        return 0
    else:
        print("✗ Some checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
