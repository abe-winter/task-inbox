import uuid, json
from datetime import datetime
from typing import List, Optional
import sqlalchemy
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

class Base(Model):
    __abstract__ = True
    id: uuid.UUID = Column(UUID, primary_key=True, default=uuid.uuid4)
    created: datetime = Column(DateTime, default=func.now())

class TaskSchema(Base):
    "container for a group of task types"
    name: str = Column(String, primary_key=True)

class ApiKey(Base):
    "a key which external providers use to call in"
    key: str = Column(primary_key=True)
    tschema_id: Optional[uuid.UUID] = Column(UUID, ForeignKey('taskschema.name'), nullable=True) # recommended to restrict this to a specific provider, but not required
    tschema = relationship('TaskSchema')
    permissions: List[str] = Column(JSONB)
    active: bool = Column(Boolean, default=True)
    name: Optional[str] = Column(String, nullable=True) # non-unique

class WebhookKey(Base):
    "a key to use for outbound webhooks for a specific provider"
    tschema_id: str = Column(ForeignKey('taskschema.name'))
    tschema = relationship('TaskSchema')
    key: str = Column(String)
    active: bool = Column(Boolean, default=True)

    # __table_args__ = (
    #     UniqueConstraint('tschema_id', 'key'),
    # )

class SchemaVersion(Base):
    "container for a specific version of an external app's task list"
    tschema_id: str = Column(ForeignKey('taskschema.name'))
    tschema = relationship('TaskSchema')
    version: int = Column(Integer) # internal version to track updates
    semver: str = Column(String) # external version string from provider
    default_hook_url: Optional[str] = Column(String, nullable=True)
    hook_auth: Optional[str] = Column(String, nullable=True) # colon-sep string of [(header, query), item_name]. ex: header:apikey, query:key

    # __table_args__ = (
    #     UniqueConstraint('tschema_id', 'version'),
    #     UniqueConstraint('tschema_id', 'semver'),
    # )

class TaskType(Base):
    "within a SchemaVersion, a named task"
    version_id: uuid.UUID = Column(UUID, ForeignKey('schemaversion.id'))
    version = relationship('SchemaVersion')
    name: str = Column(String)
    pending_states: List[str] = Column(JSONB)
    resolved_states: List[str] = Column(JSONB)

    # todo: hook_url + hook_auth that overrides the one for the schema
    # todo: permission spec. role to view, role to edit, role to access specific states

    # __table_args__ = (
    #     UniqueConstraint('version_id', 'name'),
    # )

class Task(Base):
    "an instance of a TaskType"
    ttype_id: uuid.UUID = Column(UUID, ForeignKey('tasktype.id'))
    ttype = relationship('TaskType')
    state: Optional[str] = Column(String, nullable=True)
    # user_id: Optional[uuid.UUID] = Column(UUID, default=None, ForeignKey('user.id')) # assigned user
    resolved: bool = Column(Boolean, default=False)

class TaskHistory(Base):
    "task changelog"
    task_id: uuid.UUID = Column(UUID, ForeignKey('task.id'))
    task = relationship('Task')
    state: Optional[str] = Column(String, nullable=True)
    resolved: bool = Column(Boolean, default=False)
    # editor_id: Optional[uuid.UUID] = Column(default=None, ForeignKey('user.id')) # null here means inbound or some CLI actions
    # assigned_id: Optional[uuid.UUID] = Column(default=None, ForeignKey('user.id')) # assigned user
    update_meta: Optional[dict] = Column(JSONB, nullable=True)
