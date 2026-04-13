from pydantic import BaseModel
from typing import Optional

class AchievementBase(BaseModel):
    name: str
    description: Optional[str] = None
    xp_reward: int = 0
    coin_reward: int = 0

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(AchievementBase):
    pass

class Achievement(AchievementBase):
    id: int
    
    class Config:
        from_attributes = True
