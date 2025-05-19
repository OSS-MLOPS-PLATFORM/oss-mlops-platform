from pydantic import BaseModel, Field
from typing import List, Union

### Forward Request API
class Forward(BaseModel):
    name: str = Field(alias = 'name')
    address: str = Field(alias = 'address')
    port: str = Field(alias = 'port')

class Forwarding_Request(BaseModel):
    user: str = Field(alias = 'user')
    imports: Union[List[Forward], List[None]] = Field(alias = 'imports')
    exports: Union[List[Forward], List[None]] = Field(alias = 'exports')
###