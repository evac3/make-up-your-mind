import React from 'react';
import { View, Text, TextInput, TextInputProps, StyleSheet } from 'react-native';
import { useTheme } from '../../hooks/useTheme';

interface Props extends TextInputProps {
  label?: string;
  error?: string;
  editable?: boolean;
}

export const Input: React.FC<Props> = ({
  label,
  error,
  editable = true,
  style,
  ...rest
}) => {
  const { colors, isLargeText } = useTheme();

  return (
    <View style={styles.container}>
      {label && <Text style={[styles.label, { color: colors.subtext }]}>{label}</Text>}
      <TextInput
        editable={editable}
        placeholderTextColor={colors.subtext}
        style={[
          styles.input,
          {
            backgroundColor: editable ? colors.card : '#F2F2F7',
            borderColor: error ? '#FF3B30' : colors.border,
            color: editable ? colors.text : colors.subtext,
          },
          isLargeText && styles.largeFont,
          style,
        ]}
        {...rest}
      />
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { width: '100%', gap: 6 },
  label: { fontSize: 13, fontWeight: '600', textTransform: 'uppercase' },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
  },
  largeFont: { fontSize: 20 },
  errorText: { color: '#FF3B30', fontSize: 12, marginTop: 2 },
});