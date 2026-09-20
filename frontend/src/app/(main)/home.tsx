import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { DuckLarge } from '../../components/duck/DuckLarge';
import { ChatInput } from '../../components/chat/ChatInput';
import { SpeechButton } from '../../components/chat/SpeechButton';
import { TopMenu } from '../../components/ui/TopMenu';
import { useConversationStore } from '../../store/conversationStore';

export default function HomeScreen() {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const startNewConversation = useConversationStore((s) => s.startNewConversation);

  const handleSend = (text: string) => {
    const id = startNewConversation(text);
    router.replace({
        pathname: '/(main)/conversation/[id]',
        params: { id },
    } as any);
  };

  const handleSpeech = () => {
    // Simulated speech transcription hook
    handleSend('Should I accept the new job offer or stay at my current role?');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => setMenuOpen(true)}>
          <Ionicons name="ellipsis-horizontal-circle-sharp" size={40} color="#455099"/>
        </TouchableOpacity>
      </View>

      {/* Main Character Large & Centered */}
      <View style={styles.centerArea}>
        <DuckLarge />
      </View>

      {/* Input Directly Below + Large Round Speech Button Below That */}
      <View style={styles.inputArea}>
        <ChatInput onSend={handleSend} />
        <SpeechButton onPress={handleSpeech} />
      </View>

      <TopMenu visible={menuOpen} onClose={() => setMenuOpen(false)} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fbf5e5', justifyContent: 'space-between' },
  header: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    height: 50,
  },
  centerArea: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  inputArea: { paddingHorizontal: 20, paddingBottom: 100, alignItems: 'center', gap: 16 },
});