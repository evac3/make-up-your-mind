import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';

// 1. Import your local full duck image asset
const DuckFullImg = require('../../../assets/images/duck_full.png');

export const DuckLarge = () => (
  <View style={styles.container}>
    <Text style={styles.label}>Type or push to speak and ask me anything!</Text>
    <View style={styles.circle}>
      <Image 
        source={DuckFullImg} 
        style={styles.duckImage}
        resizeMode="cover"
      />
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: { alignItems: 'center', marginVertical: 24 },
  circle: {
    width: 300,
    height: 300,
    borderRadius: 70,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    elevation: 4,
    marginTop: 24,
  },
  duckImage: {
    width: '100%',
    height: '100%',
  },
  label: { marginTop: 12, fontSize: 18, fontWeight: '700', color: '#455099' },
});