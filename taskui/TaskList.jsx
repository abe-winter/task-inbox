import React from 'react';
import useSWR from 'swr';
import { format, formatRelative } from 'date-fns';
import { useStore } from './store';
import { ErrorBoundary } from './components.jsx';

export function TaskListItem({ task, types }) {
  const setTaskId = useStore(state => state.setTaskId);
  return <div className="list-group-item" onClick={() => setTaskId(task.id)}>
    <input type="checkbox" className="form-check-input" checked={task.resolved} readOnly />
    <span className="ms-2"><strong>
      {types[task.ttype_id]?.name || task.ttype_id}
    </strong></span>
    <span className="ms-2">{task.state}</span>
    <span className="ms-2 text-muted">
      {formatRelative(new Date(task.created), new Date())}
    </span>
  </div>;
}

export function TaskList() {
  const { data, error, isLoading } = useSWR('/api/v1/tasks', async () => {
    const res = await fetch('/api/v1/tasks');
    if (res.status == 200) return await res.json();
    throw Error(`${res.status} ${await res.text()}`);
  });
  return <div>
    <h4 className="d-none d-md-block">Task list</h4>
    <div className="alert alert-secondary">todo filter settings</div>
    {isLoading ? <div>Loading ...</div>
      : error ? <div className="alert alert-danger">{error.toString()}</div>
      : <div className="list-group">
        {data.tasks.map(task => (<ErrorBoundary key={task.id}>
          <TaskListItem task={task} types={data.types} />
        </ErrorBoundary>))}
      </div>
    }
  </div>;
}
