import React, { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { ScreenWrapper } from '../../../components/layout/ScreenWrapper';
import { useConversationStore } from '../../../store/conversationStore';

export default function NewConversationScreen() {
  const router = useRouter();
  const startNewConversation = useConversationStore((s) => s.startNewConversation);

  useEffect(() => {
    const id = startNewConversation('Help me make a quick decision.');
    router.replace(`/(main)/conversation/${id}`);
  }, [router, startNewConversation]);

  return <ScreenWrapper style={{ backgroundColor: '#FFFFFF' }} />;
}