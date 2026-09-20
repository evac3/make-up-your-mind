import React from 'react';
import { StyleSheet, ViewStyle } from 'react-native';
import { SafeAreaView, Edge } from 'react-native-safe-area-context';
import { useTheme } from '../../hooks/useTheme';

interface Props {
  children?: React.ReactNode;
  style?: ViewStyle;
  edges?: Edge[];
}

export const ScreenWrapper: React.FC<Props> = ({
  children,
  style,
  edges = ['top', 'bottom', 'left', 'right'],
}) => {
  const { colors } = useTheme();

  return (
    <SafeAreaView
      edges={edges}
      style={[styles.container, { backgroundColor: colors.background }, style]}
    >
      {children}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
  },
});