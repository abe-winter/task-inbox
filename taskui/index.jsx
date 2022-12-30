import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { TaskList } from './TaskList.jsx';
import { SingleTask } from './SingleTask.jsx';
import { useStore } from './store';

function TaskUi(props) {
  const taskId = useStore(state => state.taskId);
  // todo: some kind of auth check boundary
  return <div className="container">
    <div className="row">
      <div className="col-md-4 mb-2">
        <TaskList />
      </div>
      <div className="col">
        <SingleTask taskId={taskId} />
      </div>
    </div>
  </div>;
}

createRoot(document.querySelector('#app')).render(<TaskUi />);
