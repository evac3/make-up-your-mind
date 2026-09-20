import { useCallback } from 'react';
import { useConversationStore } from '../store/conversationStore';
import { useSpeech } from './useSpeech';

export const useConversation = (conversationId?: string) => {
  const conversations = useConversationStore((s) => s.conversations);
  const startNewConversation = useConversationStore((s) => s.startNewConversation);
  const addMessage = useConversationStore((s) => s.addMessage);
  const { speak } = useSpeech();

  const conversation = conversations.find((c) => c.id === conversationId);

  const sendMessage = useCallback(
    (text: string) => {
      if (!conversationId) return;

      addMessage(conversationId, 'user', text);

      setTimeout(() => {
        const duckResponses = [
          'Quack! What are your top 3 criteria for deciding this?',
          'If you flip a coin and it lands on Option A, are you relieved or disappointed?',
          'What is the worst-case scenario if you go with your gut on this?',
        ];
        const reply = duckResponses[Math.floor(Math.random() * duckResponses.length)];
        addMessage(conversationId, 'ai', reply);
        speak(reply);
      }, 700);
    },
    [conversationId, addMessage, speak]
  );

  return {
    conversation,
    messages: conversation?.messages ?? [],
    sendMessage,
    startNewConversation,
  };
};