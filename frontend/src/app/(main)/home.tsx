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
      {/* Top Bar with RED home text and right menu */}
      <View style={styles.header}>
        <Text style={styles.homeText}>Home</Text>
        <TouchableOpacity onPress={() => setMenuOpen(true)}>
          <Ionicons name="ellipsis-horizontal-circle-sharp" size={32} color="#1C1C1E" />
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
  container: { flex: 1, backgroundColor: '#FFFFFF', justifyContent: 'space-between' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    height: 50,
  },
  homeText: { color: 'red', fontSize: 22, fontWeight: '800' },
  centerArea: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  inputArea: { paddingHorizontal: 20, paddingBottom: 24, alignItems: 'center', gap: 16 },
});