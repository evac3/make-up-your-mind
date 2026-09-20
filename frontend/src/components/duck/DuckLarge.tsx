import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const DuckLarge = () => (
  <View style={styles.container}>
    <View style={styles.circle}>
      <Text style={styles.duckText}>🦆</Text>
    </View>
    <Text style={styles.label}>Decision Duck</Text>
  </View>
);

const styles = StyleSheet.create({
  container: { alignItems: 'center', marginVertical: 24 },
  circle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#FFE600',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  duckText: { fontSize: 72 },
  label: { marginTop: 12, fontSize: 18, fontWeight: '700', color: '#1C1C1E' },
});