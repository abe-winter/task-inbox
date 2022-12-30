import flask
from flask import render_template
from flask_appbuilder import BaseView, ModelView, ModelRestApi, MasterDetailView, expose
from flask_appbuilder.api import BaseApi, protect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import select, text
from .main import appbuilder, db # yes circular but it's from their boilerplate
from .models import Task, TaskType, SchemaVersion, TaskSchema, TaskHistory

class TasksListView(ModelView):
    datamodel = SQLAInterface(Task)
    # todo: TaskType show name
    # todo: filter list by type, resolved
    label_columns = {'ttype': 'Type'}
    list_columns = ['ttype', 'state', 'user_id', 'resolved', 'created']
    edit_exclude_columns = ['created', 'ttype']
    add_exclude_columns = ['created']
    # todo: dropdown for editing state instead of freeform

appbuilder.add_view(TasksListView, 'Tasks')

class TasksRest(BaseApi):
    resource_name = 'tasks'

    @expose('/<task_id>/history')
    @protect(allow_browser_login=True)
    def get_history(self, task_id):
        "get task history"
        # todo: page / limit history
        session = appbuilder.get_session()
        query = select(TaskHistory).order_by('created').join(Task).filter_by(id=task_id)
        return {
            'history': [
                row.jsonable()
                for row, in session.execute(query)
            ]
        }

    @expose('/<task_id>/state', methods=['PATCH'])
    @protect(allow_browser_login=True)
    def patch_state(self, task_id):
        # `or None` because empty string nullifies
        state = flask.request.args['state'] or None
        session = appbuilder.get_session()
        task = session.get(Task, task_id)
        if task.state != state:
            task.state = state
            task.editor_id = flask.g.user.id
            task.resolved = task.ttype.state_resolved(state, crash=True) if state else False
            session.add(task)
            session.add(TaskHistory.from_task(task))
            session.commit()
        return {'task': task.jsonable()}

    @expose('/')
    @protect(allow_browser_login=True)
    def get_list(self):
        # todo: paging
        # todo: filter type, resolved, assigned
        resolved = flask.request.args.get('resolved')
        schema_name = flask.request.args.get('schema')
        ttype_name = flask.request.args.get('ttype')
        session = appbuilder.get_session()
        # todo: figure out n+1 / join load here
        query = select(Task).order_by(text('created')).join(TaskType).join(SchemaVersion).join(TaskSchema)
        rows = [row for row, in session.execute(query)]
        return {
            'tasks': [row.jsonable() for row in rows],
            'types': {
                str(row.ttype_id): {'schema_name': row.ttype.version.tschema.name, **row.ttype.jsonable()}
                for row in rows
            },
        }

appbuilder.add_api(TasksRest)

class TaskUi(BaseView):
    @expose('')
    def list(self):
        # todo: auth / redirect
        return self.render_template('taskui.htm')

appbuilder.add_view(TaskUi, 'task ui')

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    "Application wide 404 error handler"
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
