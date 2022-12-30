import create from 'zustand';

export const useStore = create((set) => ({
  task: null,
  setTask: (task) => set((state) => ({ task })),
}));
