import { useSettingsStore } from '../store/settingsStore';

export const useTheme = () => {
  const darkMode = useSettingsStore((s) => s.settings.darkMode);
  const largeText = useSettingsStore((s) => s.settings.accessibility.largeText);

  const colors = darkMode
    ? {
        background: '#455099',
        card: '#455099',
        text: '#fbf5e5',
        subtext: '#f18aac',
        border: '#455099',
        primary: '#8A2BE2',
        secondary: '#007AFF',
      }
    : {
        background: '#fbf5e5',
        card: '#fbf5e5',
        text: '#455099',
        subtext: '#f18aac',
        border: '#fbf5e5',
        primary: '#8A2BE2',
        secondary: '#007AFF',
      };

  return {
    isDark: darkMode,
    isLargeText: largeText,
    colors
  };
};