import create from 'zustand';

export const useStore = create((set) => ({
  taskId: null,
  setTaskId: (taskId) => set((state) => ({ taskId })),
}));
