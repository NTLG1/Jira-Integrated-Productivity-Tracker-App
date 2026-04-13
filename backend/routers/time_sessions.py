from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud
from ..database import get_db
from ..schemas import TimeSession, TimeSessionCreate, TimeSessionUpdate

router = APIRouter()

@router.get("/time-sessions/", response_model=List[TimeSession])
def read_time_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    time_sessions = crud.get_time_sessions(db, skip=skip, limit=limit)
    return time_sessions

@router.get("/time-sessions/active/", response_model=List[TimeSession])
def read_active_time_sessions(task_id: int = Query(None), db: Session = Depends(get_db)):
    """Get active (non-ended) time sessions"""
    if task_id:
        # Get active time session for specific task
        time_sessions = crud.get_active_time_sessions_by_task(db, task_id=task_id)
    else:
        # Get all active time sessions
        time_sessions = crud.get_active_time_sessions(db)
    return time_sessions

@router.get("/time-sessions/{time_session_id}", response_model=TimeSession)
def read_time_session(time_session_id: int, db: Session = Depends(get_db)):
    db_time_session = crud.get_time_session(db, time_session_id=time_session_id)
    if db_time_session is None:
        raise HTTPException(status_code=404, detail="Time session not found")
    return db_time_session

@router.post("/time-sessions/", response_model=TimeSession)
def create_time_session(time_session: TimeSessionCreate, db: Session = Depends(get_db)):
    return crud.create_time_session(db=db, time_session=time_session)

@router.put("/time-sessions/{time_session_id}", response_model=TimeSession)
def update_time_session(time_session_id: int, time_session: TimeSessionUpdate, db: Session = Depends(get_db)):
    db_time_session = crud.get_time_session(db, time_session_id=time_session_id)
    if db_time_session is None:
        raise HTTPException(status_code=404, detail="Time session not found")
    return crud.update_time_session(db=db, db_time_session=db_time_session, time_session=time_session)

@router.delete("/time-sessions/{time_session_id}")
def delete_time_session(time_session_id: int, db: Session = Depends(get_db)):
    db_time_session = crud.get_time_session(db, time_session_id=time_session_id)
    if db_time_session is None:
        raise HTTPException(status_code=404, detail="Time session not found")
    return crud.delete_time_session(db=db, time_session_id=time_session_id)
