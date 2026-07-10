from pydantic import BaseModel, Field
from typing import List

### Configuration API
class Object_Store(BaseModel):
    used_client: str = Field(alias = 'used-client')
    pre_auth_url: str = Field(alias = 'pre-auth-url')
    pre_auth_token: str = Field(alias = 'pre-auth-token')
    user_domain_name: str = Field(alias = 'user-domain-name')
    project_domain_name: str = Field(alias = 'project-domain-name')
    project_name: str = Field(alias = 'project-name')
    auth_version: str = Field(alias = 'auth-version')
    bucket_prefix: str = Field(alias = 'bucket-prefix')

class Cloud(BaseModel):
    platforms: List[str] = Field(alias = 'platforms')

class Storage(BaseModel):
    platforms: List[str] = Field(alias = 'platforms')
    object_store: Object_Store = Field(alias = 'object-store')
    
class HPC(BaseModel):
    platforms: List[str] = Field(alias = 'platforms')

class Integration(BaseModel):
    platforms: List[str] = Field(alias = 'platforms')

class Enviroments(BaseModel):
    secrets_path: str = Field(alias = 'secrets-path')
    cloud: Cloud = Field(alias = 'cloud')
    storage: Storage = Field(alias = 'storage')
    hpc: HPC = Field(alias = 'hpc')
    integration: Integration = Field(alias = 'integration')

class Configuration(BaseModel):
    ice_id: str = Field(alias = 'ice-id')
    enviroment: Enviroments = Field(alias = 'enviroments')
###