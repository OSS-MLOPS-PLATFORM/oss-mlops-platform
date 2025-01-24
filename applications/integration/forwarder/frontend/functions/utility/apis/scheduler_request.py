from pydantic import BaseModel, Field
from typing import List

### Job API
class Scheduler_Request(BaseModel):
    task_times: List[str] = Field(alias = 'task-times')
###