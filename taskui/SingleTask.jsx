import React from 'react';
import { useStore } from './store';

export function SingleTask({ taskId }) {
  return taskId == null
    ? <div className="alert alert-info">No task selected</div>
    : <div>
      <div className="alert alert-warning">todo render task {taskId}</div>
      <div className="alert alert-warning">todo load history</div>
    </div>;
}
