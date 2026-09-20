export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  traits: string[];
}

export interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

export interface AppSettings {
  darkMode: boolean;
  notifications: {
    email: boolean;
    sms: boolean;
    app: boolean;
  };
  accessibility: {
    largeText: boolean;
    textToSpeech: boolean;
  };
  saveChats: boolean;
}