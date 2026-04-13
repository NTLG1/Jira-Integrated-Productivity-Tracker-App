from sqlalchemy import Column, Integer, String, Text, Boolean
from ..database import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    xp_reward = Column(Integer, default=0)
    coin_reward = Column(Integer, default=0)
