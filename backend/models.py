import uuid, os
from typing import Optional, List
from datetime import datetime
from pydantic import constr
from sqlmodel import SQLModel, Field, create_engine, UniqueConstraint, Column
from sqlalchemy.dialects.postgresql import JSONB

class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(primary_key=True)
    name: str

class TaskSchema(SQLModel, table=True):
    "container for a group of task types"
    name: str = Field(primary_key=True, max_length=64)
    created: datetime

class ApiKey(SQLModel, table=True):
    "a key which external providers use to call in"
    key: str = Field(primary_key=True)
    tschema_id: Optional[str] = Field(default=None, foreign_key='taskschema.name') # recommended to restrict this to a specific provider, but not required
    permissions: List[str] = Field(default=[])
    active: bool = True
    name: Optional[str] # non-unique
    created: datetime

class WebhookKey(SQLModel, table=True):
    "a key to use for outbound webhooks for a specific provider"
    id: Optional[uuid.UUID] = Field(primary_key=True)
    tschema_id: str = Field(foreign_key='taskschema.name')
    key: str
    active: bool = True
    created: datetime

    __table_args__ = (
        UniqueConstraint('tschema_id', 'key'),
    )

class SchemaVersion(SQLModel, table=True):
    "container for a specific version of an external app's task list"
    id: Optional[uuid.UUID] = Field(primary_key=True)
    tschema_id: str = Field(foreign_key='taskschema.name')
    version: int # internal version to track updates
    semver: str # external version string from provider
    default_hook_url: Optional[str]
    hook_auth: Optional[str] # colon-sep string of [(header, query), item_name]. ex: header:apikey, query:key
    created: datetime

    __table_args__ = (
        UniqueConstraint('tschema_id', 'version'),
        UniqueConstraint('tschema_id', 'semver'),
    )

class TaskType(SQLModel, table=True):
    "within a SchemaVersion, a named task"
    id: Optional[uuid.UUID] = Field(primary_key=True)
    version_id: uuid.UUID = Field(foreign_key='schemaversion.id')
    name: str
    pending_states: List[str]
    resolved_states: List[str]
    # todo: hook_url + hook_auth
    # todo: permission spec. role to view, role to edit, role to access specific states

    __table_args__ = (
        UniqueConstraint('version_id', 'name'),
    )

class Task(SQLModel, table=True):
    "an instance of a TaskType"
    id: Optional[uuid.UUID] = Field(primary_key=True)
    ttype_id: uuid.UUID = Field(foreign_key='tasktype.id')
    state: Optional[str]
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key='user.id') # assigned user
    resolved: bool = False
    created: datetime

class TaskHistory(SQLModel, table=True):
    "task changelog"
    id: Optional[uuid.UUID] = Field(primary_key=True)
    task_id: uuid.UUID = Field(foreign_key='task.id')
    state: Optional[str]
    resolved: bool
    editor_id: Optional[uuid.UUID] = Field(default=None, foreign_key='user.id') # null here means inbound or some CLI actions
    assigned_id: Optional[uuid.UUID] = Field(default=None, foreign_key='user.id') # assigned user
    update_meta: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    created: datetime

engine = create_engine(os.environ['SQLALCHEMY_URL'])
