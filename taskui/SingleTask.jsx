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
  const taskUrl = useStore(state => state.taskUrl);
  const { mutate } = useSWRConfig();
  async function setState() {
    const { task } = await setTaskState(taskId, label);
    setLocalTaskState(taskId, label, task.resolved);
    mutate(historyUrl);
    mutate(taskUrl, null, {
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
        submitted {format(new Date(task.created), 'PPPPppp')}
      </div>
      <hr />
      <h5>Set state</h5>
      <div style={{ fontSize: 'x-large' }}>
        <StateBtn taskId={task.id} label={''} historyUrl={historyUrl} resolved={false} />
        {task.type.pending_states.map(state => <StateBtn key={state} taskId={task.id} label={state} historyUrl={historyUrl} resolved={false} disabled={state == task.state} />)}
        {task.type.resolved_states.map(state => <StateBtn key={state} taskId={task.id} label={state} historyUrl={historyUrl} resolved={true} disabled={state == task.state} />)}
      </div>
      {data?.history[0]?.update_meta != null && <>
        <hr />
        <table className="table"><tbody>
          {Object.entries(data.history[0].update_meta).map(([key, val]) => <MetaRow key={key} field={key} val={val} />)}
        </tbody></table>
      </>}
    </div></div>
    {isLoading ? <div>Loading history ...</div>
      : error ? <div className="alert alert-danger">{error.toString()}</div>
      : <div className="">
        {data.history.slice(1).map(update => <HistoryCard key={update.id} update={update} />)}
      </div>}
  </div>;
}

function HistoryCard({ update, i }) {
  return (<div className="mb-2">
    <div className="row">
      <div className="col-md">
        state {update.state ? <b>{update.state}</b> : <span className="text-muted">unset</span>}
      </div>
      <div className="col-md">
        <div className="text-muted">{format(new Date(update.created), 'Pppp')}</div>
      </div>
    </div>
  </div>);
}

function MetaRow({ field, val }) {
  const [keyName, keyType] = field.split('__');
  return (<tr>
    <td>{keyName}</td>
    <td>{keyType == 'preview' ? <a href={val}>{val}</a> : val}</td>
  </tr>);
}
