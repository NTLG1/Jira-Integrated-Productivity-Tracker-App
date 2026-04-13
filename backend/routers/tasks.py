from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..crud import task as crud_task
from ..database import get_db
from ..schemas import Task, TaskCreate, TaskUpdate

router = APIRouter()

@router.get("/tasks/", response_model=List[Task])
def read_tasks(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if user_id:
        tasks = crud_task.get_tasks_by_user(db, user_id=user_id, skip=skip, limit=limit)
    else:
        tasks = crud_task.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud_task.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud_task.create_task(db=db, task=task)

@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud_task.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud_task.update_task(db=db, db_task=db_task, task=task)

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud_task.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Clear Jira fields if they exist
    if db_task.jira_issue_key:
        db_task.jira_issue_key = None
        db_task.jira_project_key = None
        db_task.jira_url = None
        db_task.is_jira_imported = False
        db.commit()
        db.refresh(db_task)
    
    return crud_task.delete_task(db=db, task_id=task_id)

@router.delete("/tasks/{task_id}/jira")
def delete_task_jira_issue(task_id: int, db: Session = Depends(get_db)):
    """
    Delete the associated Jira issue for a task
    """
    db_task = crud_task.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if this task has a Jira issue
    if not db_task.jira_issue_key:
        raise HTTPException(status_code=400, detail="Task does not have a Jira issue")
    
    # In a real implementation, this would call the Jira API to delete the issue
    # For now, we'll just clear the Jira fields
    db_task.jira_issue_key = None
    db_task.jira_project_key = None
    db_task.jira_url = None
    db_task.is_jira_imported = False
    
    db.commit()
    db.refresh(db_task)
    
    return {"message": "Jira issue deleted successfully", "task": db_task}

