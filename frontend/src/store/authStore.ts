import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useProfileStore } from './profileStore';

interface AuthState {
  isAuthenticated: boolean;
  signup: (payload: { name: string; email: string; phone: string; password: string }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      signup: ({ name, email, phone }) => {
        useProfileStore.getState().initProfile({ name, email, phone });
        set({ isAuthenticated: true });
      },
      logout: () => set({ isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);