import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppSettings } from '../types';

interface SettingsState {
  settings: AppSettings;
  updateSettings: (updater: (prev: AppSettings) => AppSettings) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: {
        darkMode: false,
        notifications: { email: true, sms: false, app: true },
        accessibility: { largeText: false, textToSpeech: false },
        saveChats: true,
      },
      updateSettings: (updater) =>
        set((state) => ({ settings: updater(state.settings) })),
    }),
    {
      name: 'settings-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);