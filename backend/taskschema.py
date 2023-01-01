from typing import Optional, List, Literal
import pydantic

class TaskType(pydantic.BaseModel):
    name: str
    resolved_states: List[str]
    pending_states: List[str] = pydantic.Field(default_factory=list)

class HookAuth(pydantic.BaseModel):
    kind: Literal['head']
    val: str # header name probably
    args: Optional[dict]

class TaskSchemaSchema(pydantic.BaseModel):
    name: str # todo: figure out disambig or prefixing for global collisions
    semver: str
    default_hook_url: Optional[str]
    hook_auth: Optional[HookAuth]
    tasktypes: List[TaskType]
