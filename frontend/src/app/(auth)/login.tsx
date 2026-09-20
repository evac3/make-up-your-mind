import React, { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenWrapper } from '../../components/layout/ScreenWrapper';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/authStore';

export default function LoginScreen() {
  const router = useRouter();
  const signup = useAuthStore((s: { signup: any; }) => s.signup);

  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    if (!emailOrPhone.trim() || !password.trim()) return;
    signup({
      name: 'User',
      email: emailOrPhone.includes('@') ? emailOrPhone : `${emailOrPhone}@user.app`,
      phone: emailOrPhone.includes('@') ? '+10000000000' : emailOrPhone,
      password,
    });
    router.replace('/(main)/home');
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.keyboardContainer}
    >
      <ScreenWrapper>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>Welcome Back</Text>
          <Text style={styles.subtitle}>Log in to consult Make Up Your Mind</Text>

          <View style={styles.form}>
            <Input
              label="Email or Phone"
              value={emailOrPhone}
              onChangeText={setEmailOrPhone}
              placeholder="name@email.com or phone"
              autoCapitalize="none"
            />
            <Input
              label="Password"
              value={password}
              onChangeText={setPassword}
              placeholder="Enter your password"
              secureTextEntry
            />
            <Button label="Sign In" variant="primary" onPress={handleLogin} />
            <Button
              label="New here? Create profile"
              variant="ghost"
              onPress={() => router.push('/(auth)/signup')}
            />
          </View>
        </ScrollView>
      </ScreenWrapper>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  keyboardContainer: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: 'center', alignItems: 'center' },
  mascot: { fontSize: 50, marginBottom: 8 },
  title: { fontSize: 26, fontWeight: '800', color: '#455099' },
  subtitle: { fontSize: 14, color: '#f18aac', marginTop: 4, marginBottom: 24 },
  form: { width: '100%', gap: 14 },
});