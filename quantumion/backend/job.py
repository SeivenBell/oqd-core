from typing import Optional

from pydantic import BaseModel

########################################################################################

from quantumion.backend.task import Task, TaskResult

########################################################################################

class Job(BaseModel):
    job_id: str
    task: Task
    backend: str
    status: str
    result: Optional[TaskResult] = None
