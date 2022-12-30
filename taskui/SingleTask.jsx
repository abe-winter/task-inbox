import React from 'react';
import useSWR from 'swr';
import { format } from 'date-fns';
import { useStore } from './store';
import { fetcher } from './components.jsx';

async function setTaskState(taskId, label) {
  console.log('set task state', taskId, label);
  // todo: set global state (if still selected) and reload history
}

function StateBtn({ taskId, label, resolved }) {
  return <button className={`badge m-2 text-bg-${resolved ? 'success' : 'secondary'}`} onClick={setTaskState}>
    {resolved ? '✅ ' : ''}{label}
  </button>;
}

export function SingleTask({ task }) {
  if (task == null)
    return <div className="alert alert-info">No task selected</div>;
  const { data, error, isLoading } = useSWR(`/api/v1/tasks/${task.id}/history`, fetcher);
  // todo: merge meta blobs instead of showing first
  return <div>
    <div className="card mb-2"><div className="card-body">
      <h4>
        {task.type.name}
        <span className="ms-2 badge text-bg-primary">{task.state}</span>
      </h4>
      <div className="text-muted">
        {format(new Date(task.created), 'PPPPpppp')}
      </div>
      <hr />
      <h5>Set state</h5>
      <div style={{ fontSize: 'x-large' }}>
        {task.type.pending_states.map(state => <StateBtn key={state} taskId={task.id} label={state} resolved={false} disabled={state == task.state} />)}
        {task.type.resolved_states.map(state => <StateBtn key={state} taskId={task.id} label={state} resolved={true} disabled={state == task.state} />)}
      </div>
    </div></div>
    {isLoading ? <div>Loading history ...</div>
      : error ? <div className="alert alert-danger">{error.toString()}</div>
      : <div className="">
        {data.history[0]?.update_meta != null && <div className="card"><div className="card-body">
          <h5>Metadata</h5>
          <table className="table"><tbody>
            <tr>
              <th>Field</th>
              <th>Value</th>
            </tr>
            {Object.entries(data.history[0].update_meta).map(renderMetaRow)}
          </tbody></table>
        </div></div>}
        {data.history.slice(1).map((update, i) => <div className="card"><div className="card-body">
          todo render history diff {i} {JSON.stringify(update)}
        </div></div>)}
      </div>}
  </div>;
}

function renderMetaRow([key, val]) {
  const [keyName, keyType] = key.split('__');
  return (<tr key={key}>
    <td>{keyName}</td>
    <td>{keyType == 'preview' ? <a href={val}>{val}</a> : val}</td>
  </tr>);
}
