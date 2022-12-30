import React from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { format } from 'date-fns';
import { useStore } from './store';
import { fetcher } from './components.jsx';

async function setTaskState(taskId, state) {
  const res = await fetch(`/api/v1/tasks/${taskId}/state?` + new URLSearchParams({ state }), { method: 'PATCH' });
  if (res.status != 200) throw Error(`${res.status} ${await res.text()}`);
  return await res.json();
}

function StateBtn({ taskId, label, resolved, historyUrl }) {
  const setLocalTaskState = useStore(state => state.setTaskState);
  const { mutate } = useSWRConfig();
  async function setState() {
    const { task } = await setTaskState(taskId, label);
    setLocalTaskState(taskId, label, task.resolved);
    mutate(historyUrl);
    mutate('/api/v1/tasks', null, {
      populateCache: (newVal, oldData) => ({
        ...oldData,
        tasks: oldData.tasks.map(item => item.id == taskId ? task : item),
      }),
      revalidate: false,
    });
  }
  return <button className={`badge m-2 text-bg-${label == '' ? 'light' : resolved ? 'success' : 'secondary'}`} onClick={setState}>
    {resolved ? '✅ ' : ''}{label || 'unset'}
  </button>;
}

export function SingleTask({ task }) {
  if (task == null)
    return <div className="alert alert-info">No task selected</div>;
  const historyUrl = `/api/v1/tasks/${task.id}/history`;
  const { data, error, isLoading } = useSWR(historyUrl, fetcher);
  // todo: merge meta blobs instead of showing first
  return <div>
    <div className="card mb-2"><div className="card-body">
      <h4>
        <input type="checkbox" className="form-check-input me-2" checked={task.resolved} readOnly />
        {task.type.name}
        <span className="ms-2 badge text-bg-primary">{task.state}</span>
      </h4>
      <div className="text-muted">
        {format(new Date(task.created), 'PPPPppp')}
      </div>
      <hr />
      <h5>Set state</h5>
      <div style={{ fontSize: 'x-large' }}>
        <StateBtn taskId={task.id} label={''} historyUrl={historyUrl} resolved={false} />
        {task.type.pending_states.map(state => <StateBtn key={state} taskId={task.id} label={state} historyUrl={historyUrl} resolved={false} disabled={state == task.state} />)}
        {task.type.resolved_states.map(state => <StateBtn key={state} taskId={task.id} label={state} historyUrl={historyUrl} resolved={true} disabled={state == task.state} />)}
      </div>
    </div></div>
    {isLoading ? <div>Loading history ...</div>
      : error ? <div className="alert alert-danger">{error.toString()}</div>
      : <div className="">
        {data.history[0]?.update_meta != null && <div className="card mb-2"><div className="card-body">
          <h5>Metadata</h5>
          <table className="table"><tbody>
            <tr>
              <th>Field</th>
              <th>Value</th>
            </tr>
            {Object.entries(data.history[0].update_meta).map(renderMetaRow)}
          </tbody></table>
        </div></div>}
        {data.history.slice(1).map((update, i) => <div key={update.id} className="card mb-2"><div className="card-body">
          state <b>{update.state || '(unset)'}</b>
          <div className="text-muted">{format(new Date(update.created), 'Pppp')}</div>
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
