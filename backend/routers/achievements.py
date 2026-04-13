from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud
from ..database import get_db
from ..schemas import Achievement, AchievementCreate, AchievementUpdate

router = APIRouter()

@router.get("/achievements/", response_model=List[Achievement])
def read_achievements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    achievements = crud.get_achievements(db, skip=skip, limit=limit)
    return achievements

@router.get("/achievements/{achievement_id}", response_model=Achievement)
def read_achievement(achievement_id: int, db: Session = Depends(get_db)):
    db_achievement = crud.get_achievement(db, achievement_id=achievement_id)
    if db_achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return db_achievement

@router.post("/achievements/", response_model=Achievement)
def create_achievement(achievement: AchievementCreate, db: Session = Depends(get_db)):
    return crud.create_achievement(db=db, achievement=achievement)
