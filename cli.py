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

COMMANDS = Dictorator(injectors=[Injector('session', 'Session', dbsession)])

class DryRun(Exception):
    "early-exit which prevents saving transaction"

@COMMANDS
def rmschema(name: str, dryrun: bool = False):
    "remove a named schema from db"
    from sqlalchemy import text, select
    from app.models import TaskSchema
    with dbsession() as session:
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

@COMMANDS
def taskschema(path: str, dryrun: bool = False):
    "set a task schema from yaml file"
    import yaml
    from sqlalchemy import text, select
    from backend.taskschema import TaskSchemaSchema
    from app.models import TaskSchema, SchemaVersion, TaskType
    blob = yaml.safe_load(open(path))
    schema = TaskSchemaSchema.parse_obj(blob)
    logger.info('parsed schema %s version %s with %d tasks', schema.name, schema.semver, len(schema.tasktypes))
    with dbsession() as session:
        existing = session.execute(schema_name=schema.name).first()
        new_ver = SchemaVersion(
            version=0,
            semver=schema.semver,
            default_hook_url=schema.default_hook_url,
            hook_auth=schema.hook_auth,
        )
        if not existing:
            logger.info('creating new schema + version 0')
            row = TaskSchema(id=uuid.uuid4(), name=schema.name)
            session.add(row)
            new_ver.tschema_id = row.id
            session.add(new_ver)
        else:
            old_ver, = existing
            logger.info('%s has old version %d', schema.name, old_ver.version)
            new_ver.tschema_id = old_ver.tschema_id
            new_ver.version = old_ver.version + 1
            session.add(new_ver)
        for ttype in schema.tasktypes:
            # todo: is new_ver.id right here? if yes remove id= force in TaskSchema above
            session.add(TaskType(
                version_id=new_ver.id,
                name=ttype.name,
                pending_states=ttype.pending_states,
                resolved_states=ttype.resolved_states,
            ))
        logger.info('inserted %d tasktypes', len(schema.tasktypes))
        if dryrun:
            raise DryRun
        session.commit()

@COMMANDS
def schemas(session: 'Session'):
    "list schemas"
    from sqlalchemy import select
    from app.models import TaskSchema
    rows = session.execute(select(TaskSchema))
    print('rows', rows)

@COMMANDS
def tasks(schema_name: str):
    "list tasks in schema"
    from sqlalchemy import select
    from app.models import TaskType, SchemaVersion, TaskSchema
    with dbsession() as session:
        rows = session.execute
        raise NotImplementedError

@COMMANDS
def mktask(schema_name: str, task_name: str):
    "insert a task"
    from sqlalchemy import select
    from app.models import TaskType, SchemaVersion, TaskSchema
    with dbsession() as session:
        query = SchemaVersion.latest(select(TaskType).filter_by(name=task_name), schema_name=schema_name)
        print(query)
    raise NotImplementedError

if __name__ == '__main__':
    COMMANDS.main()
