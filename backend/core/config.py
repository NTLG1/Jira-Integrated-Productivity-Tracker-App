from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gamified Productivity App"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str
    
    # Jira settings
    JIRA_URL: str | None = None
    JIRA_EMAIL: str | None = None
    JIRA_API_TOKEN: str | None = None
    JIRA_DEFAULT_PROJECT: str = "KAN"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
