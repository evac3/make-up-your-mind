import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';

interface Props {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Button: React.FC<Props> = ({
  label,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  style,
  textStyle,
}) => {
  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.base,
        styles[variant],
        disabled && styles.disabledButton,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'ghost' ? '#8A2BE2' : '#FFFFFF'} />
      ) : (
        <Text
          style={[
            styles.baseText,
            styles[`${variant}Text` as keyof typeof styles],
            disabled && styles.disabledText,
            textStyle,
          ]}
        >
          {label}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  primary: { backgroundColor: '#8A2BE2' },
  secondary: { backgroundColor: '#007AFF' },
  ghost: { backgroundColor: 'transparent' },
  danger: { backgroundColor: '#FF3B30' },
  disabledButton: { backgroundColor: '#E5E5EA' },
  baseText: { fontSize: 16, fontWeight: '700' },
  primaryText: { color: '#FFFFFF' },
  secondaryText: { color: '#FFFFFF' },
  ghostText: { color: '#8A2BE2' },
  dangerText: { color: '#FFFFFF' },
  disabledText: { color: '#8E8E93' },
});