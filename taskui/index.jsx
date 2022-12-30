import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { TaskList } from './TaskList.jsx';
import { SingleTask } from './SingleTask.jsx';
import { useStore } from './store';

function TaskUi(props) {
  const task = useStore(state => state.task);
  // todo: some kind of auth check boundary
  return <div className="container-xl">
    <div className="row">
      <div className="col-md-5 mb-2">
        <TaskList />
      </div>
      <div className="col">
        <SingleTask task={task} />
      </div>
    </div>
  </div>;
}

createRoot(document.querySelector('#app')).render(<TaskUi />);
