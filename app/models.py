import uuid, json
from datetime import datetime
from typing import List, Optional
import sqlalchemy
from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime, ForeignKey, Boolean, UniqueConstraint
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
    tschema_id: str = Column(ForeignKey('task_schema.id'))
    tschema = relationship('TaskSchema')
    key: str = Column(String)
    active: bool = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('tschema_id', 'key'),
    )

class SchemaVersion(Base):
    "container for a specific version of an external app's task list"
    tschema_id: str = Column(ForeignKey('task_schema.id'))
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
    def latest(cls, query: 'Optional[sqlalchemy.sql.Select]' = None, schema_name: Optional[str] = None) -> 'sqlalchemy.sql.Select':
        "extend a query to use the latest schema version. optionally also specify the schema name"
        # todo: use inner select instead of join().limit(1) so it doesn't force the cardinality of the other tables to be 1
        query = query or sqlalchemy.select(cls)
        query = query.join(cls).order_by(sqlalchemy.text('version desc')).limit(1)
        if schema_name:
            query = query.join(TaskSchema).where(TaskSchema.name == schema_name)
        return query

class TaskType(Base):
    "within a SchemaVersion, a named task"
    version_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('schema_version.id'))
    version = relationship('SchemaVersion')
    name: str = Column(String)
    pending_states: List[str] = Column(JSONB)
    resolved_states: List[str] = Column(JSONB)

    # todo: hook_url + hook_auth that overrides the one for the schema
    # todo: permission spec. role to view, role to edit, role to access specific states

    __table_args__ = (
        UniqueConstraint('version_id', 'name'),
    )

class Task(Base):
    "an instance of a TaskType"
    ttype_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('task_type.id'))
    ttype = relationship('TaskType')
    state: Optional[str] = Column(String, nullable=True)
    user_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id'), nullable=True) # assigned user
    resolved: bool = Column(Boolean, default=False)

class TaskHistory(Base):
    "task changelog"
    task_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey('task.id'))
    task = relationship('Task')
    state: Optional[str] = Column(String, nullable=True)
    resolved: bool = Column(Boolean, default=False)
    editor_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id'), nullable=True) # null here means inbound or some CLI actions
    assigned_id: Optional[int] = Column(Integer, ForeignKey('ab_user.id'), nullable=True) # assigned user
    update_meta: Optional[dict] = Column(JSONB, nullable=True)
