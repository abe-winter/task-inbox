import yaml, logging
from flask_appbuilder.forms import DynamicForm, FileUploadField, FieldConverter
from flask import flash
from flask_appbuilder import SimpleFormView
from flask_babel import lazy_gettext as _
import flask
from flask import render_template
from flask_appbuilder import BaseView, ModelView, ModelRestApi, MasterDetailView, expose
from flask_appbuilder.api import BaseApi, protect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import select, text
from .main import appbuilder, db # yes circular but it's from their boilerplate
from .models import Task, TaskType, SchemaVersion, TaskSchema, TaskHistory
from .auth import apikey_auth
from .messagetypes import PostTask
from .webhooks import run_webhook
from wtforms import Form, StringField
from backend.taskschema import TaskSchemaSchema

logger = logging.getLogger(__name__)

class SchemaVersionView(ModelView):
    datamodel = SQLAInterface(SchemaVersion)
    search_exclude_columns = ['hook_auth']
    list_columns = ['tschema', 'version', 'semver', 'default_hook_url', 'hook_auth']
    label_columns = {'tschema': 'schema name'}
    add_columns = ['tschema']
    # list_columns = ['ttype', 'state', 'user_id', 'resolved', 'created']
    # edit_exclude_columns = ['created', 'ttype']
    # add_exclude_columns = ['created']

appbuilder.add_view(SchemaVersionView, 'Schemas')

def insert_schema(session: 'sqlalchemy.orm.Session', fileobj: 'io.IOWrapper'):
    "helper to insert a yaml schema to db as new version"
    schema = TaskSchemaSchema.parse_obj(yaml.safe_load(fileobj))
    logger.info('parsed schema %s version %s with %d tasks', schema.name, schema.semver, len(schema.tasktypes))
    existing = session.execute(SchemaVersion.latest(schema.name)).first()
    new_ver = SchemaVersion(
        version=0,
        semver=schema.semver,
        default_hook_url=schema.default_hook_url,
        hook_auth=schema.hook_auth and schema.hook_auth.dict(),
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

class NewSchemaVersion(DynamicForm):
    yaml_body = FileUploadField('yaml schema spec')

class NewSchemaView(SimpleFormView):
    form = NewSchemaVersion
    form_title = 'Upload new schema'
    message = 'Uploaded'

    def form_post(self, form):
        session = appbuilder.get_session
        insert_schema(session, form.yaml_body.data.stream)
        session.commit()

appbuilder.add_view(NewSchemaView, "New schema")
