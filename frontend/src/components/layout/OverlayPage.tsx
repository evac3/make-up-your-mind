import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { ScreenWrapper } from './ScreenWrapper';
import { useTheme } from '../../hooks/useTheme';

interface Props {
  title: string;
  children: React.ReactNode;
  onClose?: () => void;
}

export const OverlayPage: React.FC<Props> = ({ title, children, onClose }) => {
  const router = useRouter();
  const { colors } = useTheme();

  const handleClose = () => {
    if (onClose) {
      onClose();
    } else {
      router.replace('/(main)/home');
    }
  };

  return (
    <ScreenWrapper style={[styles.wrapper, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
        <TouchableOpacity
          onPress={handleClose}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
          style={styles.closeButton}
        >
          <Ionicons name="close" size={26} color={colors.text} />
        </TouchableOpacity>
      </View>
      <View style={styles.body}>{children}</View>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  wrapper: { paddingHorizontal: 0 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  title: { fontSize: 20, fontWeight: '700' },
  closeButton: { padding: 4 },
  body: { flex: 1 },
});