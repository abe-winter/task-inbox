import pydantic
from typing import Optional

class PostTask(pydantic.BaseModel):
    "json post body for adding task via webhook"
    schema_name: str
    task: str
    state: Optional[str]
    meta: Optional[dict]
