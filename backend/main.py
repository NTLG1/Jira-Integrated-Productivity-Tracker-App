from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import tasks, users, time_sessions, achievements, jira
from .core.config import settings

# Remove the table creation from import time
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API for tracking productivity with gamification features"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(time_sessions.router, prefix=settings.API_V1_STR, tags=["time_sessions"])
app.include_router(achievements.router, prefix=settings.API_V1_STR, tags=["achievements"])
app.include_router(jira.router, prefix=settings.API_V1_STR, tags=["jira"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Productivity Tracker API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
