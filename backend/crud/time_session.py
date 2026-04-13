from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from ..models import TimeSession
from ..schemas import TimeSessionCreate, TimeSessionUpdate

def get_time_session(db: Session, time_session_id: int):
    return db.query(TimeSession).filter(TimeSession.id == time_session_id).first()

def get_time_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TimeSession).offset(skip).limit(limit).all()

def get_active_time_sessions(db: Session):
    """Get all active (non-ended) time sessions"""
    return db.query(TimeSession).filter(TimeSession.end_time.is_(None)).all()

def get_active_time_sessions_by_task(db: Session, task_id: int):
    """Get active time session for a specific task"""
    return db.query(TimeSession).filter(
        and_(
            TimeSession.task_id == task_id,
            TimeSession.end_time.is_(None)
        )
    ).all()

def create_time_session(db: Session, time_session: TimeSessionCreate):
    db_time_session = TimeSession(**time_session.dict())
    db.add(db_time_session)
    db.commit()
    db.refresh(db_time_session)
    return db_time_session

def update_time_session(db: Session, db_time_session: TimeSession, time_session: TimeSessionUpdate):
    update_data = time_session.model_dump(exclude_unset=True)
    
    # Remove any fields that shouldn't be updated
    update_data.pop('id', None)  # Ensure ID is not updated
    
    # Calculate duration if end_time is provided and start_time exists
    if 'end_time' in update_data and update_data['end_time'] is not None and db_time_session.start_time is not None:
        duration_seconds = (update_data['end_time'] - db_time_session.start_time).total_seconds()
        duration_minutes = duration_seconds / 60
        update_data['duration_minutes'] = duration_minutes
    
    for key, value in update_data.items():
        setattr(db_time_session, key, value)
    db.commit()
    db.refresh(db_time_session)
    return db_time_session

def delete_time_session(db: Session, time_session_id: int):
    db_time_session = db.query(TimeSession).filter(TimeSession.id == time_session_id).first()
    if db_time_session:
        db.delete(db_time_session)
        db.commit()
    return db_time_session
