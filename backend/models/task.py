from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from ..database import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String, nullable=False)  # "low", "medium", "high"
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # "pending", "in_progress", "completed"
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Jira integration fields
    jira_issue_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    jira_project_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    jira_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_jira_imported: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    time_sessions = relationship("TimeSession", back_populates="task")
