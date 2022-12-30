import flask
from flask import render_template
from flask_appbuilder import BaseView, ModelView, ModelRestApi, MasterDetailView, expose
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

class TasksRest(ModelRestApi):
    resource_name = 'tasks'
    datamodel = SQLAInterface(Task)
    allow_browser_login = True
    # edit_exclude_columns = ['created', 'ttype']
    # add_exclude_columns = ['created']
    list_columns = ['ttype_id', 'state', 'user_id', 'resolved', 'created']
    # todo: field permissions

    @expose('/<task_id>')
    def get(self, task_id):
        # todo: include user info
        session = appbuilder.get_session()
        query = select(Task).filter_by(id=task_id).join(TaskType)
        row, = session.execute(query).first()

        return {
            'task': task.jsonable(),
            'type': task.ttype.jsonable(),
        }

    @expose('/<task_id>/history')
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
    def patch_state(self, task_id):
        state = flask.request.args['state']
        session = appbuilder.get_session()
        task = session.get(Task, task_id)
        task.state = state or None # empty string nullifies
        task.resolved = task.ttype.state_resolved(state, crash=True) if state else False
        session.add(task)
        session.add(TaskHistory.from_task(task))
        session.commit()
        return {'task': task.jsonable()}

    @expose('/')
    def get_list(self):
        # todo: use user's auth
        # todo: paging
        # todo: filter type, resolved, assigned
        session = appbuilder.get_session()
        query = select(Task).order_by(text('created')).join(TaskType)
        rows = [row for row, in session.execute(query)]
        return {
            'tasks': [row.jsonable() for row in rows],
            'types': {
                str(row.ttype_id): row.ttype.jsonable()
                for row in rows
            },
        }

appbuilder.add_api(TasksRest)

class TaskUi(BaseView):
    @expose('/taskui')
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
