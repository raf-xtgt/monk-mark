import { Platform } from 'react-native';

// For React Native:
// - Android emulator: use 10.0.2.2 instead of localhost
// - iOS simulator: can use localhost
// - Physical device: replace with your machine's IP address (e.g., 192.168.1.x)
const getApiBaseUrl = () => {
  if (Platform.OS === 'android') {
    return 'https://83cb-103-120-202-172.ngrok-free.app/api/mm';
  }
  // iOS simulator or web
  return 'http://localhost:8000/api/mm';
};

const getWebSocketUrl = () => {
  if (Platform.OS === 'android') {
    return 'wss://83cb-103-120-202-172.ngrok-free.app/ws/voice-tutor';
  }
  // iOS simulator or web
  return 'ws://localhost:8000/ws/voice-tutor';
};

export const API_BASE_URL = getApiBaseUrl();
export const WS_TUTOR_URL = getWebSocketUrl();

export const API_CONSTANTS = {
  BASE_URL: API_BASE_URL,
  WS_BASE_URL: getWebSocketUrl(),
};
