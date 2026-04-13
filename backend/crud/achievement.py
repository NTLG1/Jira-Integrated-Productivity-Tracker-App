from sqlalchemy.orm import Session
from ..models import Achievement
from ..schemas import AchievementCreate, AchievementUpdate

def get_achievement(db: Session, achievement_id: int):
    return db.query(Achievement).filter(Achievement.id == achievement_id).first()

def get_achievements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Achievement).offset(skip).limit(limit).all()

def create_achievement(db: Session, achievement: AchievementCreate):
    db_achievement = Achievement(**achievement.dict())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement
