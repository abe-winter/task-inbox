import create from 'zustand';

export const useStore = create((set) => ({
  task: null,
  setTask: (task) => set((state) => ({ task })),
  // set task state if ID hasn't changed
  setTaskState: (taskId, newState, resolved) => set(function (state) {
    if (state.task?.id == taskId) return { task: { ...state.task, state: newState, resolved } };
    return {};
  }),
}));
