from pydantic import BaseModel, Field
from typing import List, Optional

### Job API
class Job_Depends(BaseModel):
    id: str = Field(alias = 'id')
    name: str = Field(alias = 'name')

class Job_Workflow(BaseModel):
    requires: Optional[List[Job_Depends]] = Field(alias = 'requires')
    enables: Optional[List[Job_Depends]] = Field(alias = 'enables')

class Job_Provided_File(BaseModel):
    source: str = Field(alias = 'source') 
    target: str = Field(alias = 'target')
    overwrite: bool = Field(alias = 'overwrite')

class Job_Stored_File(BaseModel):
    source: str = Field(alias = 'source') 
    target: str = Field(alias = 'target')
    remove: bool = Field(alias = 'remove')

class Job_Files(BaseModel):
    provide: Optional[List[Job_Provided_File]] = Field(alias = 'provide')
    store: Optional[List[Job_Stored_File]] = Field(alias = 'store')

class Job_Venv(BaseModel):
    name: str = Field(alias = 'name')
    directory: str = Field(alias = 'directory')
    configuration_modules: List[str] = Field(alias = 'configuration-modules')
    packages: List[str] = Field(alias = 'packages')

class Job_Enviroment(BaseModel):
    submission_modules: List[str] = Field(alias = 'submission-modules')
    venv: Job_Venv = Field(alias = 'venv')

class Job_Request(BaseModel):
    target: str = Field(alias = 'target')
    name: str = Field(alias = 'name')
    enviroment: Job_Enviroment = Field(alias = 'enviroment')
    files: Job_Files = Field(alias = 'files')
    workflow: Job_Workflow = Field(alias = 'workflow')
###