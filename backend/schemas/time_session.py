from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TimeSessionBase(BaseModel):
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    interrupted: bool = False
    notes: Optional[str] = None

class TimeSessionCreate(TimeSessionBase):
    pass

class TimeSessionUpdate(BaseModel):
    task_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    interrupted: Optional[bool] = None
    notes: Optional[str] = None

class TimeSession(TimeSessionBase):
    id: int
    
    class Config:
        from_attributes = True
