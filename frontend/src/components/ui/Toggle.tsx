import React from 'react';
import { View, Text, Switch, StyleSheet } from 'react-native';
import { useTheme } from '../../hooks/useTheme';

interface Props {
  label: string;
  value: boolean;
  onValueChange: (val: boolean) => void;
  description?: string;
}

export const Toggle: React.FC<Props> = ({ label, value, onValueChange, description }) => {
  const { colors, isLargeText } = useTheme();

  return (
    <View style={styles.container}>
      <View style={styles.textContainer}>
        <Text style={[styles.label, { color: colors.text }, isLargeText && styles.largeLabel]}>
          {label}
        </Text>
        {description && (
          <Text style={[styles.description, { color: colors.subtext }]}>{description}</Text>
        )}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#E5E5EA', true: '#8A2BE2' }}
        thumbColor="#FFFFFF"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
  },
  textContainer: { flex: 1, paddingRight: 16 },
  label: { fontSize: 16, fontWeight: '500' },
  largeLabel: { fontSize: 19 },
  description: { fontSize: 13, marginTop: 2 },
});