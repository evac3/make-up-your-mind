import { Platform } from 'react-native';

/* ==========================================================================
   Types & Models
   ========================================================================== */

export interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  traits: string[];
  createdAt: Date;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  conversationId: string;
}

export interface Conversation {
  id: string;
  userId: string;
  topic: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  preview: string;
}

export interface Settings {
  darkMode: boolean;
  largeText: boolean;
  textToSpeech: boolean;
  saveChats: boolean;
  notifications: {
    email: boolean;
    text: boolean;
    app: boolean;
  };
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

/* ==========================================================================
   Color Tokens & Themes
   ========================================================================== */

export const Colors = {
  light: {
    text: '#455099',
    background: '#fbf5e5',
    backgroundElement: '#fbf5e5',
    textSelected: '#fbf5e5',
    backgroundSelected: '#455099',
    textSecondary: '#f18aac',
  },
  dark: {
    text: '#fbf5e5',
    background: '#455099',
    backgroundElement: '#455099',
    textSelected: '#455099',
    backgroundSelected: '#fbf5e5',
    textSecondary: '#f18aac',
  },
} as const;

export type ThemeMode = keyof typeof Colors;
export type ThemeColor = keyof typeof Colors.light;

export interface Theme {
  text: string;
  background: string;
  backgroundElement: string;
  textSelected: string;
  backgroundSelected: string;
  textSecondary: string;
}

export const lightTheme: Theme = Colors.light;
export const darkTheme: Theme = Colors.dark;

// Default theme is light
export const defaultTheme: Theme = lightTheme;

/* ==========================================================================
   Typography, Spacing & Layout
   ========================================================================== */

const BASE_SIZE = 16;

export const createTypography = (largeText: boolean) => {
  const scale = largeText ? 1.2 : 1;
  return {
    xs: BASE_SIZE * 0.75 * scale,
    sm: BASE_SIZE * 0.875 * scale,
    base: BASE_SIZE * scale,
    lg: BASE_SIZE * 1.125 * scale,
    xl: BASE_SIZE * 1.25 * scale,
    '2xl': BASE_SIZE * 1.5 * scale,
    '3xl': BASE_SIZE * 1.875 * scale,
    fontFamily: Platform.select({
      ios: 'System',
      android: 'Roboto',
      default: 'System',
    }),
    fontWeights: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
    },
  };
};

export const Fonts = Platform.select({
  ios: {
    sans: 'system-ui',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80, default: 0 });
export const MaxContentWidth = 800;