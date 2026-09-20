import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Conversation, Message } from '../types';
import { useSettingsStore } from './settingsStore';

interface ConversationState {
  conversations: Conversation[];
  activeConversationId: string | null;
  startNewConversation: (initialText: string) => string;
  addMessage: (convId: string, sender: 'user' | 'ai', text: string) => void;
  setActiveConversation: (id: string | null) => void;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      conversations: [],
      activeConversationId: null,

      startNewConversation: (initialText) => {
        const id = Date.now().toString();
        const initialMsg: Message = {
          id: `${id}-1`,
          sender: 'user',
          text: initialText,
          timestamp: Date.now(),
        };
        const aiReply: Message = {
          id: `${id}-2`,
          sender: 'ai',
          text: "Quack! Let's break this down. What are your key choices?",
          timestamp: Date.now() + 500,
        };

        const newConv: Conversation = {
          id,
          title: initialText.length > 25 ? initialText.substring(0, 25) + '...' : initialText,
          messages: [initialMsg, aiReply],
          createdAt: Date.now(),
        };

        const shouldSave = useSettingsStore.getState().settings.saveChats;
        if (shouldSave) {
          set((state) => ({
            conversations: [newConv, ...state.conversations],
            activeConversationId: id,
          }));
        } else {
          set({ activeConversationId: id });
        }
        return id;
      },

      addMessage: (convId, sender, text) => {
        const newMsg: Message = {
          id: Date.now().toString(),
          sender,
          text,
          timestamp: Date.now(),
        };
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === convId ? { ...c, messages: [...c.messages, newMsg] } : c
          ),
        }));
      },

      setActiveConversation: (id) => set({ activeConversationId: id }),
    }),
    {
      name: 'conversation-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);