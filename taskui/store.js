import create from 'zustand';

export const baseTaskUrl = '/api/v1/tasks';

export const useStore = create((set) => ({
  task: null,
  setTask: (task) => set((state) => ({ task })),

  // set nested task state if ID hasn't changed
  // todo: look for fancy nested key setter in zustand
  setTaskState: (taskId, newState, resolved) => set(function (state) {
    if (state.task?.id == taskId) return { task: { ...state.task, state: newState, resolved } };
    return {};
  }),

  taskUrl: `${baseTaskUrl}?resolved=un`,
  setTaskUrl: taskUrl => set((state) => ({ taskUrl })),
}));
