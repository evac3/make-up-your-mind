import React from 'react';
import { TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  onPress: () => void;
  isListening?: boolean;
}

export const SpeechButton: React.FC<Props> = ({ onPress, isListening }) => (
  <TouchableOpacity
    activeOpacity={0.8}
    onPress={onPress}
    style={[styles.button, isListening && styles.listening]}
  >
    <Ionicons name={isListening ? 'radio' : 'mic'} size={36} color="#fbf5e5" />
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  button: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#455099',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#455099',
    shadowOpacity: 0.35,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 6,
  },
  listening: { backgroundColor: '#f18aac' },
});