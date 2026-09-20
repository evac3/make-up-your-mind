import { useSettingsStore } from '../store/settingsStore';

export const useTheme = () => {
  const darkMode = useSettingsStore((s) => s.settings.darkMode);
  const largeText = useSettingsStore((s) => s.settings.accessibility.largeText);

  const colors = darkMode
    ? {
        background: '#121212',
        card: '#1E1E1E',
        text: '#FFFFFF',
        subtext: '#8E8E93',
        border: '#2C2C2E',
        primary: '#8A2BE2',
        secondary: '#007AFF',
      }
    : {
        background: '#FAF9F6',
        card: '#FFFFFF',
        text: '#1C1C1E',
        subtext: '#636366',
        border: '#E5E5EA',
        primary: '#8A2BE2',
        secondary: '#007AFF',
      };

  return {
    isDark: darkMode,
    isLargeText: largeText,
    colors,
  };
};