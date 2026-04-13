from sqlalchemy import Column, Float, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class TimeSession(Base):
    __tablename__ = "time_sessions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Float)
    interrupted = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationships
    task = relationship("Task", back_populates="time_sessions")
