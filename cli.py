#!/usr/bin/env python3
import argparse, functools, inspect, asyncio, os, logging, json
from backend.dictorator import Dictorator
# note: most imports are inside functions because this does a lot and needs to control startup time

logger = logging.getLogger(__name__)
COMMANDS = Dictorator()

def dbsession():
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
    from backend.models import engine
    return AsyncSession(AsyncEngine(engine))

@COMMANDS
async def taskschema(path: str, dryrun: bool = False):
    "set a task schema from yaml file"
    import yaml
    from sqlalchemy.orm import Load
    from sqlmodel import select
    from backend.taskschema import TaskSchemaSchema
    from backend.models import TaskSchema, SchemaVersion, TaskType
    blob = yaml.safe_load(open(path))
    schema = TaskSchemaSchema.parse_obj(blob)
    logger.info('parsed schema %s version %s with %d tasks', schema.name, schema.semver, len(schema.tasktypes))
    async with dbsession() as session:
        # todo: order-limit the joined-load
        query = select(TaskSchema) \
            .filter_by(name=schema.name) \
            .options(Load(TaskSchema).joinedload('versions'))
        existing = (await session.execute(query)).first()
        if existing:
            logger.info('existing row found, incrementing from old version')
        if dryrun:
            logger.info('this is a dry run, quitting before DB write')
            return
        new_ver = SchemaVersion(
            tschema_id=schema.name,
            version=0,
            semver=schema.semver,
            default_hook_url=schema.default_hook_url,
            hook_auth=schema.hook_auth,
        )
        if not existing:
            row = TaskSchema(name=schema.name)
            session.add(row)
            session.add(new_ver)
            logger.info('created schema + version')
        else:
            maxver = max(ver.version for ver in existing[0].versions)
            logger.info('%s has %d existing versions with maxver %d', schema.name, len(existing[0].versions), maxver)
            if any(ver.semver == new_ver.semver for ver in existing[0].versions):
                raise KeyError(new_ver.semver, f'duplicate semver {new_ver.semver}')
            new_ver.version = maxver + 1
            session.add(new_ver)
        for ttype in schema.tasktypes:
            # print('pending', ttype.pending_states, json.dumps(ttype.pending_states))
            # print('resolved', ttype.resolved_states, json.dumps(ttype.resolved_states))
            print('ttype', TaskType(
                version_id=new_ver.id,
                name=ttype.name,
                # sigh no json support really
                pending_states=json.dumps(ttype.pending_states),
                resolved_states=json.dumps(ttype.resolved_states),
            ))
            session.add(TaskType(
                version_id=new_ver.id,
                name=ttype.name,
                # sigh no json support really
                pending_states=json.dumps(ttype.pending_states),
                resolved_states=json.dumps(ttype.resolved_states),
            ))
            raise NotImplementedError
        await session.commit()

def mkargs():
    p = argparse.ArgumentParser()
    COMMANDS.register_subparsers(p.add_subparsers(dest='command', required=True))
    return p

def main():
    args = mkargs().parse_args()
    logging.basicConfig(level=logging.INFO)
    fn = COMMANDS[args.command]
    fnargs = {
        name: getattr(args, name)
        for name in inspect.getfullargspec(fn).args
    }
    asyncio.run(fn(**fnargs))

if __name__ == '__main__':
    main()
