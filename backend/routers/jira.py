from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..database import get_db
from ..core.config import settings
from ..schemas.jira import JiraImportRequest, JiraExportRequest
from ..schemas.task import TaskCreate
from ..models import Task
from ..models.time_session import TimeSession
from datetime import timezone
import httpx
import logging

logger = logging.getLogger(__name__)
# Uncomment to enable debug logging
logging.basicConfig(level=logging.DEBUG)

router = APIRouter(prefix="/jira", tags=["jira"])


# =========================
# IMPORT
# =========================
@router.post("/import")
def import_jira_issues(import_data: JiraImportRequest, db: Session = Depends(get_db)):
    try:
        jira_url = settings.JIRA_URL
        jira_email = settings.JIRA_EMAIL
        jira_api_token = settings.JIRA_API_TOKEN

        if not jira_url:
            logger.debug("Jira URL not configured")
            raise HTTPException(500, "Jira URL not configured")
        if not jira_email:
            logger.debug("Jira email not configured")
            raise HTTPException(500, "Jira email not configured")
        if not jira_api_token:
            logger.debug("Jira API token not configured")
            raise HTTPException(500, "Jira API token not configured")

        # ✅ FIX typing
        assert jira_url is not None
        assert jira_email is not None
        assert jira_api_token is not None

        with httpx.Client(
            base_url=jira_url,
            auth=(jira_email, jira_api_token),
            headers={"Content-Type": "application/json"}
        ) as client:

            issues = []
            project_key = import_data.project_key
            issue_keys = import_data.issue_keys
            user_id = import_data.user_id

            if not project_key or not issue_keys:
                raise HTTPException(400, "Project key and issue keys are required")

            for issue_key in issue_keys:
                try:
                    logger.debug(f"Fetching issue {issue_key}")
                    response = client.get(f"/rest/api/2/issue/{issue_key}")

                    if not response:
                        logger.debug(f"No response for {issue_key}")
                        continue

                    logger.debug(f"Status {response.status_code}")

                    if response.status_code == 200 and response.text:
                        issue_data = response.json()
                        if issue_data:
                            issues.append(issue_data)
                except Exception as e:
                    logger.debug(f"Error fetching {issue_key}: {e}")

            from ..crud import task as crud_task

            imported_tasks = []

            for issue in issues:
                if not issue:
                    continue

                fields = issue.get("fields", {})
                if not fields:
                    continue

                issue_key = issue.get("key")
                project_key = fields.get("project", {}).get("key")

                existing = db.query(Task).filter(
                    Task.jira_issue_key == issue_key,
                    Task.user_id == user_id
                ).first()

                if existing:
                    logger.debug(f"Task {issue_key} already exists")
                    continue

                priority = fields.get("priority", {})
                priority_name = priority.get("name", "medium").lower() if priority else "medium"

                jira_issue_url = f"{jira_url}/browse/{issue_key}"

                task_data = {
                    "title": fields.get("summary", "No Title"),
                    "description": fields.get("description", ""),
                    "estimated_minutes": None,
                    "priority": priority_name,
                    "user_id": user_id,

                    "jira_issue_key": issue_key,
                    "jira_project_key": project_key,
                    "jira_url": jira_issue_url,
                    "is_jira_imported": True
                }

                try:
                    task_schema = TaskCreate(**task_data)
                    created_task = crud_task.create_task(db, task_schema)
                    imported_tasks.append(created_task)
                except Exception as e:
                    logger.debug(f"Create failed {issue_key}: {e}")

            return {
                "status": "success",
                "message": f"Imported {len(imported_tasks)} tasks",
                "tasks": imported_tasks
            }

    except Exception as e:
        raise HTTPException(500, str(e))


# =========================
# EXPORT
# =========================
@router.post("/tasks/{task_id}/export-to-jira")
def export_task_to_jira(task_id: int, db: Session = Depends(get_db)):
    try:
        from ..crud import task as crud_task

        db_task = crud_task.get_task(db, task_id)
        if not db_task:
            raise HTTPException(404, "Task not found")

        jira_url = settings.JIRA_URL
        jira_email = settings.JIRA_EMAIL
        jira_api_token = settings.JIRA_API_TOKEN

        if not jira_url or not jira_email or not jira_api_token:
            raise HTTPException(500, "Jira config missing")

        # FIX typing
        assert jira_url is not None
        assert jira_email is not None
        assert jira_api_token is not None

        logger.debug(f"Exporting task {task_id}")

        if db_task.is_jira_imported and db_task.jira_issue_key:
            issue_key = db_task.jira_issue_key
            logger.debug(f"Adding worklog to {issue_key}")

            with httpx.Client(
                base_url=jira_url,
                auth=(jira_email, jira_api_token),
                headers={"Content-Type": "application/json"}
            ) as client:
                # --- UPDATE JIRA ISSUE ---
                priority_map = {
                    "lowest": "Lowest",
                    "low": "Low",
                    "medium": "Medium",
                    "high": "High",
                    "highest": "Highest"
                }

                jira_priority = priority_map.get(
                    (db_task.priority or "").lower(),
                    "Medium"
                )

                update_data = {
                    "fields": {
                        "summary": db_task.title,
                        "description": db_task.description or "",
                        "priority": {
                            "name": jira_priority
                        }
                    }
                }

                update_response = client.put(
                    f"/rest/api/2/issue/{issue_key}",
                    json=update_data
                )

                if update_response.status_code not in [200, 204]:
                    logger.error(f"Failed to update Jira issue: {update_response.text}")
                else:
                    logger.debug(f"Updated Jira issue {issue_key}")
                # --- END UPDATE ---
                time_sessions = db.query(TimeSession).filter(
                    TimeSession.task_id == db_task.id
                ).all()

                valid_sessions = []
                for session in time_sessions:
                    if session.start_time is not None and session.end_time is not None:
                        # FIX duration
                        if session.duration_minutes is None:
                            session.duration_minutes = (
                                (session.end_time - session.start_time).total_seconds() / 60
                            )
                        valid_sessions.append(session)

                exported_sessions = []
                failed_sessions = []

                for session in valid_sessions:
                    try:
                        dt = session.start_time

                        # ensure timezone-aware
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)

                        started_time = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000+0000")

                        seconds = int(round(session.duration_minutes * 60))
                        logger.debug(f"Seconds: {seconds}")
                        if seconds < 60:
                            logger.debug(f"Skipping session {session.id} because duration is less than 1 minute")
                            continue

                        worklog_data = {
                            "started": started_time,
                            "timeSpentSeconds": seconds,
                            "comment": f"Session: {session.notes or 'No notes'}"
                        }

                        response = client.post(
                            f"/rest/api/2/issue/{issue_key}/worklog",
                            json=worklog_data
                        )

                        if response.status_code in [200, 201]:
                            exported_sessions.append(session.id)
                        else:
                            logger.error(f"Jira worklog error: {response.text}")
                            failed_sessions.append(session.id)

                    except Exception as e:
                        logger.error(f"Session {session.id} failed: {e}")
                        failed_sessions.append(session.id)

                return {
                    "status": "success",
                    "message": f"Exported {len(exported_sessions)} sessions",
                    "task_id": db_task.id,
                    "exported_sessions": exported_sessions,
                    "failed_sessions": failed_sessions
                }

        else:
            logger.debug("Creating new Jira story")

            with httpx.Client(
                base_url=jira_url,
                auth=(jira_email, jira_api_token),
                headers={"Content-Type": "application/json"}
            ) as client:

                priority_map = {
                    "lowest": "Lowest",
                    "low": "Low",
                    "medium": "Medium",
                    "high": "High",
                    "highest": "Highest"
                }

                jira_priority = priority_map.get(
                    (db_task.priority or "").lower(),
                    "Medium"
                )

                project_key = db_task.jira_project_key or settings.JIRA_DEFAULT_PROJECT

                issue_data = {
                    "fields": {
                        "project": {
                            "key": project_key
                        },
                        "summary": db_task.title,
                        "description": db_task.description or "",
                        "issuetype": {"name": "Story"},
                        "priority": {
                            "name": jira_priority
                        }
                    }
                }

                response = client.post("/rest/api/2/issue/", json=issue_data)

                if response.status_code not in [200, 201]:
                    raise HTTPException(500, response.text)

                issue_key = response.json().get("key")

                db_task.jira_issue_key = issue_key
                db_task.jira_project_key = db_task.jira_project_key or settings.JIRA_DEFAULT_PROJECT
                db_task.jira_url = f"{jira_url}/browse/{issue_key}"

                db.commit()
                db.refresh(db_task)

                # AFTER creating issue → export sessions

                time_sessions = db.query(TimeSession).filter(
                    TimeSession.task_id == db_task.id
                ).all()

                valid_sessions = []
                for session in time_sessions:
                    if session.start_time is not None and session.end_time is not None:
                        if session.duration_minutes is None:
                            session.duration_minutes = (
                                (session.end_time - session.start_time).total_seconds() / 60
                            )
                        valid_sessions.append(session)

                exported_sessions = []
                failed_sessions = []

                for session in valid_sessions:
                    try:
                        dt = session.start_time

                        # ensure timezone-aware
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)

                        started_time = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000+0000")

                        seconds = int(round(session.duration_minutes * 60))
                        logger.debug(f"Seconds: {seconds}")
                        if seconds < 60:
                            logger.debug(f"Skipping session {session.id} because duration is less than 1 minute")
                            continue

                        worklog_data = {
                            "started": started_time,
                            "timeSpentSeconds": seconds,
                            "comment": f"Session: {session.notes or 'No notes'}"
                        }

                        response = client.post(
                            f"/rest/api/2/issue/{issue_key}/worklog",
                            json=worklog_data
                        )

                        if response.status_code in [200, 201]:
                            exported_sessions.append(session.id)
                        else:
                            logger.error(f"Worklog failed: {response.text}")
                            failed_sessions.append(session.id)

                    except Exception as e:
                        logger.error(f"Session {session.id} failed: {e}")
                        failed_sessions.append(session.id)

                return {
                    "status": "success",
                    "message": f"Created Jira issue {issue_key} and exported {len(exported_sessions)} sessions",
                    "jira_issue_key": issue_key,
                    "exported_sessions": exported_sessions,
                    "failed_sessions": failed_sessions
                }

    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(500, str(e))
