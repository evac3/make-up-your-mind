import { useState, useCallback } from 'react';
import * as Speech from 'expo-speech';
import { useSettingsStore } from '../store/settingsStore';

export const useSpeech = () => {
  const [isListening, setIsListening] = useState(false);
  const isTtsEnabled = useSettingsStore((s) => s.settings.accessibility.textToSpeech);

  const speak = useCallback(
    (text: string) => {
      if (!isTtsEnabled) return;
      Speech.stop();
      Speech.speak(text, {
        pitch: 1.0,
        rate: 0.95,
      });
    },
    [isTtsEnabled]
  );

  const stopSpeaking = useCallback(() => {
    Speech.stop();
  }, []);

  const listen = useCallback((onResult: (transcription: string) => void) => {
    setIsListening(true);
    // STT simulation trigger; connect native audio recorder / STT model here
    const timer = setTimeout(() => {
      setIsListening(false);
      onResult('Should I accept the new job offer or stay at my current role?');
    }, 1800);

    return () => {
      clearTimeout(timer);
      setIsListening(false);
    };
  }, []);

  return {
    isListening,
    speak,
    stopSpeaking,
    listen,
  };
};