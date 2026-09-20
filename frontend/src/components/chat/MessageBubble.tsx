import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Message } from '../../types';
import { useSettingsStore } from '../../store/settingsStore';

interface Props {
  message: Message;
}

export const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.sender === 'user';
  const largeText = useSettingsStore((s) => s.settings.accessibility.largeText);

  return (
    <View style={[styles.wrapper, isUser ? styles.userWrapper : styles.aiWrapper]}>
      <View style={[styles.bubble, isUser ? styles.purple : styles.blue]}>
        <Text style={[styles.text, largeText && styles.largeText]}>
          {message.text}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: { width: '100%', flexDirection: 'row', marginVertical: 4 },
  userWrapper: { justifyContent: 'flex-end' },
  aiWrapper: { justifyContent: 'flex-start' },
  bubble: { maxWidth: '78%', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20 },
  purple: { backgroundColor: '#8A2BE2', borderBottomRightRadius: 4 }, // Purple user message
  blue: { backgroundColor: '#007AFF', borderBottomLeftRadius: 4 },   // Blue AI message
  text: { color: '#FFFFFF', fontSize: 16, lineHeight: 22 },
  largeText: { fontSize: 20, lineHeight: 26 },
});