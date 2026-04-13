from pydantic import BaseModel
from typing import List, Optional

class JiraImportRequest(BaseModel):
    project_key: str
    issue_keys: List[str]
    user_id: int

class JiraExportRequest(BaseModel):
    task_id: int
    # Add any additional export parameters if needed
    export_type: Optional[str] = "worklog"  # worklog or story
