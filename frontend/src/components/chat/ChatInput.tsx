import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSettingsStore } from '../../store/settingsStore';

interface Props {
  onSend: (text: string) => void;
}

export const ChatInput: React.FC<Props> = ({ onSend }) => {
  const [text, setText] = useState('');
  const largeText = useSettingsStore((s) => s.settings.accessibility.largeText);

  const handleSend = () => {
    if (!text.trim()) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <View style={styles.wrapper}>
      <TextInput
        value={text}
        onChangeText={setText}
        placeholder="Type a message or question..."
        placeholderTextColor="#f18aac"
        style={[styles.input, largeText && styles.largeInput]}
        onSubmitEditing={handleSend}
        returnKeyType="send"
      />
      <TouchableOpacity onPress={handleSend} disabled={!text.trim()} style={styles.sendButton}>
        <Ionicons name="arrow-up-circle" size={32} color={text.trim() ? '#455099' : '#fbf5e5'} />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fbf5e5',
    borderColor: '#455099',
    borderWidth: 2,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  input: { flex: 1, fontSize: 16, color: '#455099', maxHeight: 100},
  largeInput: { fontSize: 20 },
  sendButton: { marginLeft: 8 },
});