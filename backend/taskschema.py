from typing import Optional, List
import pydantic

class TaskType(pydantic.BaseModel):
    name: str
    resolved_states: List[str]
    pending_states: List[str] = pydantic.Field(default_factory=list)

class TaskSchemaSchema(pydantic.BaseModel):
    name: str # todo: figure out disambig or prefixing for global collisions
    semver: str
    default_hook_url: Optional[str]
    hook_auth: Optional[str]
    tasktypes: List[TaskType]
