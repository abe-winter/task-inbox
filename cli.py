#!/usr/bin/env python3
import argparse, inspect, os, logging, json, uuid
from backend.dictorator import Dictorator, Injector
# note: most imports are inside functions because this does a lot and needs to control startup time

logger = logging.getLogger(__name__)

def dbsession() -> 'sqlalchemy.orm.Session':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    engine = create_engine(os.environ['SQLALCHEMY_URL'])
    return Session(engine)

COMMANDS = Dictorator(injectors=[Injector('session', 'sqlalchemy.orm.Session', dbsession)])

class DryRun(Exception):
    "early-exit which prevents saving transaction"

@COMMANDS
def rmschema(session: 'sqlalchemy.orm.Session', name: str, dryrun: bool = False):
    "remove a named schema from db"
    # todo: take version can be 'latest', 'all', or a semver
    from sqlalchemy import text, select
    from app.models import TaskSchema
    query = select(TaskSchema).filter_by(name=name)
    row = session.execute(query).first()
    if not row:
        logger.info('not found')
        return
    obj, = row
    logger.info('found %s %s', obj.id, obj)
    if dryrun:
        raise DryRun
    session.delete(obj)
    session.commit()
    logger.info('deleted')

@COMMANDS
def taskschema(session: 'sqlalchemy.orm.Session', path: str, dryrun: bool = False):
    "set or upgrade a task schema from yaml file"
    import yaml
    from sqlalchemy import text, select
    from backend.taskschema import TaskSchemaSchema
    from app.models import TaskSchema, SchemaVersion, TaskType
    blob = yaml.safe_load(open(path))
    schema = TaskSchemaSchema.parse_obj(blob)
    logger.info('parsed schema %s version %s with %d tasks', schema.name, schema.semver, len(schema.tasktypes))
    existing = session.execute(SchemaVersion.latest(schema.name)).first()
    new_ver = SchemaVersion(
        version=0,
        semver=schema.semver,
        default_hook_url=schema.default_hook_url,
        hook_auth=schema.hook_auth,
    )
    if not existing:
        logger.info('creating new schema + initial version')
        row = TaskSchema(name=schema.name)
        session.add(row)
        new_ver.tschema = row
        session.add(new_ver)
    else:
        old_ver, = existing
        logger.info('%s has old version %d', schema.name, old_ver.version)
        if old_ver.semver == new_ver.semver:
            raise KeyError(old_ver.semver, 'semver would collide')
        new_ver.tschema_id = old_ver.tschema_id
        new_ver.version = old_ver.version + 1
        session.add(new_ver)
    for ttype in schema.tasktypes:
        session.add(TaskType(
            version=new_ver,
            name=ttype.name,
            pending_states=ttype.pending_states,
            resolved_states=ttype.resolved_states,
        ))
    logger.info('inserted %d tasktypes', len(schema.tasktypes))
    if dryrun:
        raise DryRun
    session.commit()

@COMMANDS
def schemas(session: 'sqlalchemy.orm.Session'):
    "list schemas"
    from sqlalchemy import select
    from app.models import TaskSchema
    from app.util import table
    rows = session.execute(select(TaskSchema))
    table([('name', 'created')] + [
        (row.name, row.created.date())
        for row, in rows
    ])

@COMMANDS
def tasktypes(session: 'sqlalchemy.orm.Session', schema_name: str):
    "list task types in schema"
    from sqlalchemy import select
    from app.models import TaskType, SchemaVersion, TaskSchema
    from app.util import table
    query = SchemaVersion.join_latest(schema_name, select(TaskType))
    rows = session.execute(query)
    table([('name', 'created', 'pending', 'resolved')] + [
        (row.name, row.created.date(), ','.join(row.pending_states), ','.join(row.resolved_states))
        for row, in rows
    ])

@COMMANDS
def tasks(session: 'sqlalchemy.orm.Session', schema_name: str, task_type: str):
    "list tasks of type in schema"
    # note: this includes all schema versions; add way to filter latest only? may not matter
    from sqlalchemy import select
    from app.models import TaskType, TaskSchema, Task, SchemaVersion
    from app.util import table
    query = select(Task) \
        .join(TaskType).filter_by(name=task_type) \
        .join(SchemaVersion) \
        .join(TaskSchema).filter_by(name=schema_name)
    rows = session.execute(query)
    table([('id', 'created', 'state', 'resolved')] + [
        (row.id, row.created.strftime('%m/%d %H:%M'), row.state, row.resolved)
        for row, in rows
    ])

@COMMANDS
def mktask(session: 'sqlalchemy.orm.Session', schema_name: str, task_name: str, meta: str = 'null', state: str = None):
    "insert a task to the specified schema + type. meta should be json-parseable"
    from sqlalchemy import select
    from app.models import TaskType, SchemaVersion, TaskHistory, TaskHistory, Task
    query = SchemaVersion.join_latest(schema_name, select(TaskType).filter_by(name=task_name))
    ttype, = session.execute(query).first()
    logger.info('found type %s', ttype.name)
    Task.make(session, ttype, state, json.loads(meta))
    session.commit()
    logger.info('created task and history')

@COMMANDS
def post_task(host='http://localhost:5000', schema_name='ti:sample', task_name='flag-content', key_var='LOCAL_INBOUND_API_KEY'):
    "post a task via webhook"
    import requests # note, dev-only in Pipfile
    from app.messagetypes import PostTask
    body = PostTask(schema_name=schema_name, task=task_name)
    if key_var not in os.environ:
        raise KeyError(key_var, 'not found in environment; create a key with ./cli.py api_key and set it in secrets.env')
    res = requests.post(f'{host}/api/v1/tasks/', json=body.dict(), headers={'api-key': os.environ[key_var]})
    res.raise_for_status()
    body = res.json()
    logger.info('ok %s %s', body['id'], body)

@COMMANDS
def api_key(session: 'sqlalchemy.orm.Session', schema_name: str = None, name: str = None, keylen: int = 12):
    "make an API key"
    import secrets
    from sqlalchemy import select
    from app.models import ApiKey, TaskSchema
    task_schema = None
    if schema_name:
        task_schema, = session.execute(select(TaskSchema).filter_by(name=schema_name)).first()
        logger.info('found task schema %s', task_schema)
    key = secrets.token_urlsafe(keylen)
    print('your new key is', key)
    session.add(ApiKey(key=key, tschema=task_schema, name=name))
    session.commit()
    logger.info('key created')

if __name__ == '__main__':
    COMMANDS.main()
