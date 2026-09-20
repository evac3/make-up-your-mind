import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenWrapper } from '../../components/layout/ScreenWrapper';
import { Button } from '../../components/ui/Button';

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <ScreenWrapper style={styles.container}>
      <View style={styles.heroSection}>
        <View style={styles.mascotCircle}>
          <Text style={styles.mascotText}>🦆</Text>
        </View>
        <Text style={styles.title}>Decision Duck</Text>
        <Text style={styles.subtitle}>
          Your soundboard for big crossroads, trade-offs, and everyday choices.
        </Text>
      </View>

      <View style={styles.actionSection}>
        <Button
          label="Create My Profile"
          variant="primary"
          onPress={() => router.push('/(auth)/signup')}
        />
        <Button
          label="I Already Have an Account"
          variant="ghost"
          onPress={() => router.push('/(auth)/login')}
        />
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: { justifyContent: 'space-between', paddingVertical: 32 },
  heroSection: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 12 },
  mascotCircle: {
    width: 130,
    height: 130,
    borderRadius: 65,
    backgroundColor: '#FFE600',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  mascotText: { fontSize: 68 },
  title: { fontSize: 30, fontWeight: '800', color: '#1C1C1E', textAlign: 'center' },
  subtitle: {
    fontSize: 16,
    color: '#636366',
    textAlign: 'center',
    marginTop: 10,
    lineHeight: 22,
    maxWidth: 290,
  },
  actionSection: { width: '100%', gap: 12 },
});