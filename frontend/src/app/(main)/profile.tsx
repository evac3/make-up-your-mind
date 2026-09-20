import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useProfileStore } from '../../store/profileStore';

export default function ProfileScreen() {
  const router = useRouter();
  const profile = useProfileStore((s) => s.profile);
  const updateName = useProfileStore((s) => s.updateName);
  const addTrait = useProfileStore((s) => s.addTrait);
  const removeTrait = useProfileStore((s) => s.removeTrait);

  const [name, setName] = useState(profile.name);
  const [password, setPassword] = useState('');
  const [traitInput, setTraitInput] = useState('');

  const handleAddTrait = () => {
    if (!traitInput.trim()) return;
    addTrait(traitInput.trim());
    setTraitInput('');
  };

  const handleSave = () => {
    updateName(name);
    router.replace('/(main)/home');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Profile</Text>
        <TouchableOpacity onPress={() => router.replace('/(main)/home')}>
          <Ionicons name="close" size={28} color="#1C1C1E" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.group}>
          <Text style={styles.label}>Name (Editable)</Text>
          <TextInput style={styles.input} value={name} onChangeText={setName} />
        </View>

        <View style={styles.group}>
          <Text style={styles.label}>Password (Editable)</Text>
          <TextInput
            style={styles.input}
            placeholder="New password"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
        </View>

        <View style={styles.group}>
          <Text style={styles.label}>Email (Locked)</Text>
          <TextInput style={[styles.input, styles.locked]} value={profile.email} editable={false} />
        </View>

        <View style={styles.group}>
          <Text style={styles.label}>Phone (Locked)</Text>
          <TextInput style={[styles.input, styles.locked]} value={profile.phone} editable={false} />
        </View>

        {/* Traits Section */}
        <View style={styles.group}>
          <Text style={styles.label}>Decision Traits</Text>
          <View style={styles.traitRow}>
            <TextInput
              style={[styles.input, { flex: 1 }]}
              value={traitInput}
              onChangeText={setTraitInput}
              placeholder="e.g. Risk-taker, Analytical"
            />
            <TouchableOpacity style={styles.addBtn} onPress={handleAddTrait}>
              <Text style={styles.addBtnText}>Add</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.chips}>
            {profile.traits.map((trait, index) => (
              <View key={index} style={styles.chip}>
                <Text style={styles.chipText}>{trait}</Text>
                <TouchableOpacity onPress={() => removeTrait(index)}>
                  <Ionicons name="close-circle" size={16} color="#636366" />
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </View>

        <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
          <Text style={styles.saveText}>Save Changes</Text>
        </TouchableOpacity>
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
  group: { gap: 6 },
  label: { fontSize: 13, fontWeight: '600', color: '#8E8E93', textTransform: 'uppercase' },
  input: { backgroundColor: '#FFF', borderWidth: 1, borderColor: '#E5E5EA', borderRadius: 12, padding: 14, fontSize: 16 },
  locked: { backgroundColor: '#F2F2F7', color: '#8E8E93' },
  traitRow: { flexDirection: 'row', gap: 8 },
  addBtn: { backgroundColor: '#8A2BE2', paddingHorizontal: 16, borderRadius: 12, justifyContent: 'center' },
  addBtnText: { color: '#FFF', fontWeight: '700' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 6 },
  chip: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#E5E5EA', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 14 },
  chipText: { fontSize: 14 },
  saveBtn: { backgroundColor: '#007AFF', padding: 16, borderRadius: 14, alignItems: 'center', marginTop: 10 },
  saveText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
});