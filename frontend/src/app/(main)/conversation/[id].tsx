import React, { useRef } from 'react';
import { View, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { DuckSmall } from '../../../components/duck/DuckSmall';
import { MessageBubble } from '../../../components/chat/MessageBubble';
import { ChatInput } from '../../../components/chat/ChatInput';
import { SpeechButton } from '../../../components/chat/SpeechButton';
import { useConversationStore } from '../../../store/conversationStore';
import { useSettingsStore } from '../../../store/settingsStore';

export default function ConversationScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const listRef = useRef<FlatList>(null);

  const conversation = useConversationStore((s) => s.conversations.find((c) => c.id === id));
  const addMessage = useConversationStore((s) => s.addMessage);
  const settings = useSettingsStore((s) => s.settings);

  const handleSend = (text: string) => {
    if (!id) return;
    addMessage(id, 'user', text);

    // AI logic response
    setTimeout(() => {
      const reply = 'Quack! What are the primary pros and cons here?';
      addMessage(id, 'ai', reply);
      if (settings.accessibility.textToSpeech) {
        Speech.speak(reply);
      }
    }, 800);
  };

  const handleSpeech = () => {
    handleSend('Can you summarize the pros and cons for me?');
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Left: Home Button | Top Center: Shifted Small Duck */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => router.replace('/(main)/home')} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={30} color="#007AFF" />
        </TouchableOpacity>
        <DuckSmall />
        <View style={{ width: 30 }} />
      </View>

      {/* Messages */}
      <FlatList
        ref={listRef}
        data={conversation?.messages || []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        contentContainerStyle={styles.list}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Identical Assets: Chat Input + Round Speech Button */}
      <View style={styles.bottomControls}>
        <ChatInput onSend={handleSend} />
        <SpeechButton onPress={handleSpeech} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  topBar: {
    height: 56,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: '#E5E5EA',
  },
  backBtn: { padding: 4 },
  list: { padding: 16, flexGrow: 1 },
  bottomControls: { paddingHorizontal: 20, paddingBottom: 16, alignItems: 'center', gap: 12 },
});