import React from 'react';
import { View, Text, Switch, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSettingsStore } from '../../store/settingsStore';

export default function SettingsScreen() {
  const router = useRouter();
  const settings = useSettingsStore((s) => s.settings);
  const updateSettings = useSettingsStore((s) => s.updateSettings);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
        <TouchableOpacity onPress={() => router.replace('/(main)/home')}>
          <Ionicons name="close" size={28} color="#1C1C1E" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Appearance */}
        <View style={styles.card}>
          <Text style={styles.cardHeader}>Appearance</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Dark Mode</Text>
            <Switch
              value={settings.darkMode}
              onValueChange={(val) => updateSettings((s) => ({ ...s, darkMode: val }))}
            />
          </View>
        </View>

        {/* Notifications */}
        <View style={styles.card}>
          <Text style={styles.cardHeader}>Notifications</Text>
          <View style={styles.row}>
            <Text style={styles.label}>App Notifications</Text>
            <Switch
              value={settings.notifications.app}
              onValueChange={(val) =>
                updateSettings((s) => ({ ...s, notifications: { ...s.notifications, app: val } }))
              }
            />
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Email Notifications</Text>
            <Switch
              value={settings.notifications.email}
              onValueChange={(val) =>
                updateSettings((s) => ({ ...s, notifications: { ...s.notifications, email: val } }))
              }
            />
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Text Notifications</Text>
            <Switch
              value={settings.notifications.sms}
              onValueChange={(val) =>
                updateSettings((s) => ({ ...s, notifications: { ...s.notifications, sms: val } }))
              }
            />
          </View>
        </View>

        {/* Accessibility */}
        <View style={styles.card}>
          <Text style={styles.cardHeader}>Accessibility</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Large Text</Text>
            <Switch
              value={settings.accessibility.largeText}
              onValueChange={(val) =>
                updateSettings((s) => ({ ...s, accessibility: { ...s.accessibility, largeText: val } }))
              }
            />
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Text to Speech</Text>
            <Switch
              value={settings.accessibility.textToSpeech}
              onValueChange={(val) =>
                updateSettings((s) => ({ ...s, accessibility: { ...s.accessibility, textToSpeech: val } }))
              }
            />
          </View>
        </View>

        {/* Privacy */}
        <View style={styles.card}>
          <Text style={styles.cardHeader}>Privacy</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Save Chats</Text>
            <Switch
              value={settings.saveChats}
              onValueChange={(val) => updateSettings((s) => ({ ...s, saveChats: val }))}
            />
          </View>
        </View>
      </ScrollView>
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
  content: { padding: 20, gap: 16 },
  card: { backgroundColor: '#FFF', borderRadius: 14, padding: 16, gap: 12 },
  cardHeader: { fontSize: 13, fontWeight: '700', color: '#8E8E93', textTransform: 'uppercase' },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  label: { fontSize: 16, color: '#1C1C1E' },
});