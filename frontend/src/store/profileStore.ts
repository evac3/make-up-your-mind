import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { UserProfile } from '../types';

interface ProfileState {
  profile: UserProfile;
  initProfile: (data: { name: string; email: string; phone: string }) => void;
  updateName: (name: string) => void;
  addTrait: (trait: string) => void;
  removeTrait: (index: number) => void;
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      profile: { id: '', name: '', email: '', phone: '', traits: [] },
      initProfile: ({ name, email, phone }) =>
        set({ profile: { id: Date.now().toString(), name, email, phone, traits: [] } }),
      updateName: (name) =>
        set((state) => ({ profile: { ...state.profile, name } })),
      addTrait: (trait) =>
        set((state) => ({ profile: { ...state.profile, traits: [...state.profile.traits, trait] } })),
      removeTrait: (index) =>
        set((state) => ({
          profile: {
            ...state.profile,
            traits: state.profile.traits.filter((_, i) => i !== index),
          },
        })),
    }),
    {
      name: 'profile-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);