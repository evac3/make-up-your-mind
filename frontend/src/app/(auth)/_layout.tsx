import React from 'react';
import { Stack } from 'expo-router';
import { ScreenWrapper } from '../../components/layout/ScreenWrapper';

export default function AuthLayout() {
  return (
    <ScreenWrapper>
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#fbf5e5' },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="welcome" />
        <Stack.Screen name="login" />
        <Stack.Screen name="signup" />
      </Stack>
    </ScreenWrapper>
  );
}