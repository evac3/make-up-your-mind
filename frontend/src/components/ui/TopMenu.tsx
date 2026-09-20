import React from 'react';
import { View, Text, TouchableOpacity, Modal, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

interface Props {
  visible: boolean;
  onClose: () => void;
}

export const TopMenu: React.FC<Props> = ({ visible, onClose }) => {
  const router = useRouter();

  const navigateTo = (path: string) => {
    onClose();
    router.push(path as any);
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <TouchableOpacity style={styles.backdrop} activeOpacity={1} onPress={onClose}>
        <View style={styles.menu}>
          <TouchableOpacity style={styles.item} onPress={() => navigateTo('/(main)/profile')}>
            <Ionicons name="person-outline" size={20} color="#455099" />
            <Text style={styles.text}>Profile</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.item} onPress={() => navigateTo('/(main)/settings')}>
            <Ionicons name="settings-outline" size={20} color="#455099" />
            <Text style={styles.text}>Settings</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.item, styles.lastItem]}
            onPress={() => navigateTo('/(main)/saved-conversations')}
          >
            <Ionicons name="chatbubbles-outline" size={20} color="#455099" />
            <Text style={styles.text}>Saved Conversations</Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    </Modal>
  );
};

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: '#455099', justifyContent: 'flex-start', alignItems: 'flex-end' },
  menu: {
    marginTop: 64,
    marginRight: 20,
    backgroundColor: '#fbf5e5',
    borderRadius: 14,
    width: 220,
    paddingVertical: 6,
    shadowColor: '#455099',
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 8,
  },
  item: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 16, gap: 12 },
  lastItem: { borderTopWidth: StyleSheet.hairlineWidth, borderColor: '#fbf5e5' },
  text: { fontSize: 16, fontWeight: '500', color: '#455099' },
});