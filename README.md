# Productivity Tracker App

A FastAPI-based backend for a productivity tracking application.

## Project Structure

```
backend/
├── main.py                 # Main application entry point
├── database.py             # Database configuration
├── core/
│   └── config.py          # Configuration settings
├── models/                # Database models
│   ├── __init__.py
│   ├── task.py
│   ├── user.py
│   ├── time_session.py
│   ├── achievement.py
│   └── user_achievement.py
├── schemas/               # Pydantic models for API requests/responses
│   ├── __init__.py
│   ├── task.py
│   ├── user.py
│   ├── time_session.py
│   ├── jira.py
│   └── achievement.py
├── crud/                  # CRUD operations
│   ├── __init__.py
│   ├── task.py
│   ├── user.py
│   ├── time_session.py
│   └── achievement.py
├── routers/               # API routes
│   ├── __init__.py
│   ├── tasks.py
│   ├── users.py
│   ├── time_sessions.py
│   ├── achievements.py
│   └── jira.py            # JIRA import/export endpoints
├── services/              # Business logic
│   └── jira_service.py    # JIRA import/export service
└── requirements.txt       # Python dependencies
```

## Features

- **Task Management**: Create, read, update, and delete tasks
- **User Management**: User authentication and profile management
- **Time Tracking**: Track time spent on tasks with manual timers and 60-minute work/break sessions
- **Achievement System**: Gamification features for productivity
- **JIRA Integration**: Import and export tasks and time sessions to/from JIRA format
- **Confirmation Modals**: Interactive confirmation dialogs for task deletion
- **RESTful API**: Complete CRUD operations for all entities

## API Endpoints

### Tasks
- `GET /api/v1/tasks` - Get all tasks
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `POST /api/v1/tasks` - Create a new task
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

### Users
- `GET /api/v1/users` - Get all users
- `GET /api/v1/users/{user_id}` - Get a specific user
- `POST /api/v1/users` - Create a new user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

### Time Sessions
- `GET /api/v1/time_sessions` - Get all time sessions
- `GET /api/v1/time_sessions/{session_id}` - Get a specific time session
- `POST /api/v1/time_sessions` - Create a new time session
- `PUT /api/v1/time_sessions/{session_id}` - Update a time session
- `DELETE /api/v1/time_sessions/{session_id}` - Delete a time session

### Achievements
- `GET /api/v1/achievements` - Get all achievements
- `GET /api/v1/achievements/{achievement_id}` - Get a specific achievement
- `POST /api/v1/achievements` - Create a new achievement

### JIRA Integration
- `POST /api/v1/jira/import` - Import tasks and time sessions from JIRA format
- `POST /api/v1/jira/tasks/{task_id}/export-to-jira` - Export a specific task and its time sessions to JIRA format

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**:
   - Ensure PostgreSQL is running
   - Update `.env` file with your database credentials
   - Run database migrations (if applicable)

3. **Run the application**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Development

The API follows a clean architecture pattern with:
- **Models**: Database schema definitions
- **Schemas**: Pydantic models for API validation
- **CRUD**: Database operations
- **Routers**: API endpoints
- **Services**: Business logic (including JIRA service)
- **Main**: Application configuration

## JIRA Integration Details

The application includes comprehensive JIRA integration functionality:

### Export Functionality
- Export all tasks and time sessions for the current user
- Format data in JIRA-compatible JSON structure
- Include task details, time session data, and proper formatting for JIRA import

### Import Functionality
- Import tasks and time sessions from JIRA JSON format
- Validate incoming data structure
- Create/update tasks and time sessions in the database
- Handle errors and provide feedback for import operations

## License

This project is licensed under the GPL3.0 License.
