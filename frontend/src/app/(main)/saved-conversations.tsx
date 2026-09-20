import React from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useConversationStore } from '../../store/conversationStore';

export default function SavedConversationsScreen() {
  const router = useRouter();
  const conversations = useConversationStore((s) => s.conversations);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Saved Conversations</Text>
        <TouchableOpacity onPress={() => router.replace('/(main)/home')}>
          <Ionicons name="close" size={28} color="#1C1C1E" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={conversations}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/(main)/conversation/${item.id}`)}
          >
            <Text style={styles.topicBadge}>Topic</Text>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.count}>{item.messages.length} messages</Text>
          </TouchableOpacity>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FAF9F6' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: '#E5E5EA',
  },
  title: { fontSize: 20, fontWeight: '700' },
  list: { padding: 16, gap: 12 },
  card: { backgroundColor: '#FFF', padding: 16, borderRadius: 14, borderWidth: 1, borderColor: '#E5E5EA' },
  topicBadge: { fontSize: 11, fontWeight: '700', color: '#8A2BE2', textTransform: 'uppercase' },
  cardTitle: { fontSize: 16, fontWeight: '600', color: '#1C1C1E', marginVertical: 4 },
  count: { fontSize: 12, color: '#8E8E93' },
});