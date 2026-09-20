import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenWrapper } from '../../components/layout/ScreenWrapper';
import { useAuthStore } from '../../store/authStore';

export default function SignupScreen() {
  const router = useRouter();
  const signup = useAuthStore((s: { signup: any; }) => s.signup);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleSignup = () => {
    if (!name || !email || !phone || !password) return;
    signup({ name, email, phone, password });
    router.replace('/(main)/home');
  };

  return (
    <ScreenWrapper> 
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.mascot}>🦆</Text>
          <Text style={styles.title}>Decision Duck Setup</Text>
          <Text style={styles.subtitle}>Enter your details to tailor your decision companion</Text>

          <View style={styles.form}>
            <TextInput placeholder="Full Name" style={styles.input} value={name} onChangeText={setName} />
            <TextInput placeholder="Email" style={styles.input} keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} />
            <TextInput placeholder="Phone Number" style={styles.input} keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
            <TextInput placeholder="Password" style={styles.input} secureTextEntry value={password} onChangeText={setPassword} />

            <TouchableOpacity style={styles.button} onPress={handleSignup}>
              <Text style={styles.buttonText}>Continue</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fbf5e5' },
  scroll: { padding: 24, justifyContent: 'center', flexGrow: 1, alignItems: 'center' },
  mascot: { fontSize: 56, marginBottom: 8 },
  title: { fontSize: 24, fontWeight: '800', color: '#455099' },
  subtitle: { fontSize: 14, color: '#f18aac', marginTop: 4, marginBottom: 24, textAlign: 'center' },
  form: { width: '100%', gap: 12 },
  input: { backgroundColor: '#fbf5e5', borderWidth: 1, borderColor: '#455099', borderRadius: 12, padding: 14, fontSize: 16 },
  button: { backgroundColor: '#fbf5e5', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#455099', fontSize: 16, fontWeight: '700' },
});