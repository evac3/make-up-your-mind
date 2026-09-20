import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const DuckSmall = () => (
  <View style={styles.circle}>
    <Text style={styles.duckText}>🦆</Text>
  </View>
);

const styles = StyleSheet.create({
  circle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFE600',
    alignItems: 'center',
    justifyContent: 'center',
  },
  duckText: { fontSize: 24 },
});