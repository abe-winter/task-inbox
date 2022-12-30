import uuid, json
from datetime import datetime
from typing import List, Optional
import sqlalchemy
from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID, BYTEA

class Base(Model):
    __abstract__ = True
    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created: datetime = Column(DateTime, default=func.now())

class TaskSchema(Base):
    "container for a group of task types"
    name: str = Column(String, unique=True)

class ApiKey(Base):
    "a key which external providers use to call in"
    key: bytes = Column(BYTEA, primary_key=True)
    tschema_id: Optional[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey('task_schema.id'), nullable=True) # recommended to restrict this to a specific provider, but not required
    tschema = relationship('TaskSchema')
    permissions: List[str] = Column(JSONB)
    active: bool = Column(Boolean, default=True)
    name: Optional[str] = Column(String, nullable=True) # non-unique

class WebhookKey(Base):
    "a key to use for outbound webhooks for a specific provider"
    tschema_id: str = Column(ForeignKey('task_schema.id', ondelete='CASCADE'))
    tschema = relationship('TaskSchema')
    key: str = Column(String)
    active: bool = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('tschema_id', 'key'),
    )

class SchemaVersion(Base):
    "container for a specific version of an external app's task list"
    tschema_id: str = Column(ForeignKey('task_schema.id', ondelete='CASCADE'))
    tschema = relationship('TaskSchema')
    version: int = Column(Integer) # internal version to track updates
    semver: str = Column(String) # external version string from provider
    default_hook_url: Optional[str] = Column(String, nullable=True)
    hook_auth: Optional[str] = Column(String, nullable=True) # colon-sep string of [(header, query), item_name]. ex: header:apikey, query:key

    __table_args__ = (
        UniqueConstraint('tschema_id', 'version'),
        UniqueConstraint('tschema_id', 'semver'),
    )

    @classmethod
    def latest(cls, schema_name: str, for_sub=False) -> 'sqlalchemy.sql.Select':
        "create query to get latest version row for named schema"
        return sqlalchemy.select(cls.id if for_sub else cls).order_by(sqlalchemy.text('version desc')).limit(1) \
            .join(TaskSchema).filter_by(name=schema_name)

    @classmethod
    def join_latest(cls, schema_name: str, query: 'Optional[sqlalchemy.sql.Select]', col='version_id') -> 'sqlalchemy.sql.Select':
        "extend a query to use the latest schema version"
        # return query.filter_by(version_id=maxver.scalar_subquery())
        return query.filter_by(**{col: cls.latest(schema_name, for_sub=True).scalar_subquery()})

class TaskType(Base):
    "within a SchemaVersion, a named task"
    version_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('schema_version.id', ondelete='CASCADE'))
    version = relationship('SchemaVersion')
    name: str = Column(String)
    pending_states: List[str] = Column(JSONB)
    resolved_states: List[str] = Column(JSONB)

    # todo: hook_url + hook_auth that overrides the one for the schema
    # todo: permission spec. role to view, role to edit, role to access specific states

    __table_args__ = (
        UniqueConstraint('version_id', 'name'),
    )

    def state_resolved(self, state: str, crash=False) -> Optional[bool]:
        "translate string state to bool resolved status. optionally crash if missing"
        if state in self.pending_states:
            return False
        elif state in self.resolved_states:
            return True
        elif crash:
            raise KeyError(state, f'not in pending {self.pending_states} or resolved {self.resolved_states}')
        return None

class Task(Base):
    "an instance of a TaskType"
    ttype_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('task_type.id', ondelete='CASCADE'))
    ttype = relationship('TaskType')
    state: Optional[str] = Column(String, nullable=True)
    user_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id', ondelete='CASCADE'), nullable=True) # assigned user
    resolved: bool = Column(Boolean, default=False)
    # todo: cache the merged history.update_meta somewhere

class TaskHistory(Base):
    "task changelog"
    task_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('task.id', ondelete='SET NULL'))
    task = relationship('Task')
    state: Optional[str] = Column(String, nullable=True)
    resolved: bool = Column(Boolean, default=False)
    editor_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id', ondelete='SET NULL'), nullable=True) # null here means inbound or some CLI actions
    assigned_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id', ondelete='SET NULL'), nullable=True) # assigned user
    update_meta: Optional[dict] = Column(JSONB, nullable=True)

    @classmethod
    def from_task(cls, task: Task, editor_id: Optional[int] = None, meta_diff: Optional[dict] = None) -> 'TaskHistory':
        return cls(
            task=task,
            state=task.state,
            resolved=task.resolved,
            editor_id=editor_id,
            assigned_id=task.user_id,
            update_meta=meta_diff,
        )
