from typing import Optional, List, Literal
import pydantic

# see sample.yml in this repo for an example schema that is parsed by this spec

class TaskType(pydantic.BaseModel):
    "a task in a schema that is post-able via API"
    name: str
    # resolved states; states that caused resolved=True. (resolved tasks are 'checked' i.e. hidden from list in UX)
    resolved_states: List[str]
    pending_states: List[str] = pydantic.Field(default_factory=list)

class HookAuth(pydantic.BaseModel):
    "this specifies how the webhook authorizes to external application servers"
    kind: Literal['head']
    val: str # header name probably
    args: Optional[dict]

class TaskSchemaSchema(pydantic.BaseModel):
    """Root object specifying a task schema (i.e. a named group of task types, with defined states, and optional webhook spec).
    You need one of these to POST /api/v1/tasks i.e. create new tasks.
    This is TaskSchemaSchema bc it specs TaskSchema in db, but mainly to avoid name collision.
    """
    name: str # todo: figure out disambig or prefixing for global collisions
    semver: str
    default_hook_url: Optional[str]
    hook_auth: Optional[HookAuth]
    tasktypes: List[TaskType]
