import yaml, logging
from flask_appbuilder.forms import DynamicForm, FileUploadField, FieldConverter
from flask import flash
from flask_appbuilder import SimpleFormView, has_access
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
from .util import UserFacingError

logger = logging.getLogger(__name__)

class NewSchemaVersion(DynamicForm):
    yaml_body = FileUploadField('yaml schema spec')

class SchemaVersionView(ModelView):
    datamodel = SQLAInterface(SchemaVersion)
    search_exclude_columns = ['hook_auth']
    list_columns = ['tschema', 'version', 'semver', 'default_hook_url', 'hook_auth']
    label_columns = {'tschema': 'schema name'}
    add_columns = ['yaml_body']
    add_form = NewSchemaVersion

    @expose("/add", methods=["GET", "POST"])
    @has_access
    def add(self):
        if flask.request.method != 'POST':
            return super().add()
        else:
            session = appbuilder.get_session
            # todo: I think refresh() writes to /static/uploads. this may work without it, test
            form = self.add_form.refresh()
            insert_schema(session, form.yaml_body.data.stream, web_mode=True)
            session.commit()
            return self.post_add_redirect()

appbuilder.add_view(SchemaVersionView, 'Schemas')

def insert_schema(session: 'sqlalchemy.orm.Session', fileobj: 'io.IOWrapper', web_mode: bool = False):
    "helper to insert a yaml schema to db as new version"
    # todo: in web_mode, make parse errors user-facing
    schema = TaskSchemaSchema.parse_obj(yaml.safe_load(fileobj))
    logger.info('parsed schema %s version %s with %d tasks', schema.name, schema.semver, len(schema.tasktypes))
    existing = session.execute(SchemaVersion.latest(schema.name)).first()
    # todo: edge case to exercise + fix in test suite: IntegrityError UniqueViolation "task_schema_name_key"
    # this happens when you delete all versions via UX, but the TaskSchema still exists
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
            if web_mode:
                raise UserFacingError(f"semver {old_ver.semver} would collide", response_code=409)
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
