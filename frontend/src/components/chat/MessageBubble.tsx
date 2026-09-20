import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { Message } from '../../types';
import { useSettingsStore } from '../../store/settingsStore';

// 1. Import the local file directly using require() and the proper relative path
const DuckIcon = require('../../../assets/images/duck_icon.png');

interface Props {
  message: Message;
}

export const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.sender === 'user';
  const largeText = useSettingsStore((s) => s.settings.accessibility.largeText);

  return (
    <View style={[styles.wrapper, isUser ? styles.userWrapper : styles.aiWrapper]}>
      {!isUser && (
        <Image 
          source={DuckIcon}
          style={styles.avatar} 
          resizeMode="cover" 
        />
      )}

      <View style={[styles.bubble, isUser ? styles.purple : styles.blue]}>
        <Text style={[styles.text, largeText && styles.largeText]}>
          {message.text}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: { 
    width: '100%', 
    flexDirection: 'row', 
    marginVertical: 4,
    alignItems: 'flex-end', 
  },
  userWrapper: { justifyContent: 'flex-end' },
  aiWrapper: { justifyContent: 'flex-start' },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 8,
    backgroundColor: '#79cbde',   
  },
  
  bubble: { maxWidth: '74%', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20 },
  purple: { backgroundColor: '#fbf5e5', borderBottomRightRadius: 4, borderWidth: 2, borderColor: '#deb2f0'}, 
  blue: { backgroundColor: '#fbf5e5', borderBottomLeftRadius: 4, borderWidth: 2, borderColor: '#79cbde'},   
  text: { color: '#455099', fontSize: 16, lineHeight: 22 },
  largeText: { fontSize: 20, lineHeight: 26 },
});
