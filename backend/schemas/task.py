from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str  # "low", "medium", "high"
    estimated_minutes: Optional[int] = None
    status: str = "pending"  # "pending", "in_progress", "completed"

class TaskCreate(TaskBase):
    user_id: int
    jira_issue_key: Optional[str] = None
    jira_project_key: Optional[str] = None
    jira_url: Optional[str] = None
    is_jira_imported: bool = False

class TaskUpdate(TaskBase):
    jira_issue_key: Optional[str] = None
    jira_project_key: Optional[str] = None
    jira_url: Optional[str] = None
    is_jira_imported: bool = False

class Task(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    jira_issue_key: Optional[str] = None
    jira_project_key: Optional[str] = None
    jira_url: Optional[str] = None
    is_jira_imported: bool = False
    
    class Config:
        from_attributes = True
