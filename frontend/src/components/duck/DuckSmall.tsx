import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';

// 1. Import your local full duck image asset
const DuckIcon = require('../../../assets/images/duck_icon.png');

export const DuckSmall = () => (
  <View style={styles.container}>
    <View style={styles.circle}>
      <Image 
        source={DuckIcon} 
        style={styles.duckImage}
        resizeMode="cover"
      />
    </View>
    <Text style={styles.label}>Decision Duck</Text>
  </View>
);

const styles = StyleSheet.create({
  container: { alignItems: 'center', marginTop: 100, marginBottom: 8,},
  circle: {
    width: 100,
    height: 100,
    borderRadius: 70,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    elevation: 4,
  },
  duckImage: {
    width: '100%',
    height: '100%',
  },
  label: { marginTop: 0, fontSize: 18, fontWeight: '700', color: '#455099' },
});