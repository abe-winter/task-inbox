import React from 'react';
import useSWR from 'swr';
import { format, formatRelative } from 'date-fns';
import { useStore } from './store';
import { ErrorBoundary, fetcher } from './components.jsx';

export function TaskListItem({ task, types }) {
  const selectedTaskId = useStore(state => state.task)?.id;
  const isSelected = task.id == selectedTaskId;
  const anySelected = selectedTaskId != null;
  const setTask = useStore(state => state.setTask);
  const ttype = types[task.ttype_id];
  return <div
    className={`list-group-item ${!isSelected && anySelected ? 'd-none d-md-block' : ''}`}
    onClick={() => isSelected ? setTask(null) : setTask({ ...task, type: ttype })}
    style={{ background: isSelected ? '#ddd' : null }}
    >
    <span style={{ width: '1em', display: 'inline-block' }}>
      {isSelected ? '>' : ' '}
    </span>
    <input type="checkbox" className="form-check-input" checked={task.resolved} readOnly />
    <span className="ms-2"><strong>
      {ttype == null ? task.ttype_id : `${ttype.schema_name} ${ttype.name}`}
    </strong></span>
    <span className="ms-2 badge text-bg-secondary">{task.state}</span>
    <div className="ms-2 text-muted">
      {formatRelative(new Date(task.created), new Date())}
    </div>
  </div>;
}

export function TaskList() {
  const { data, error, isLoading } = useSWR('/api/v1/tasks', fetcher);
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
