/**
 * Audio Recorder Service for React Native
 * Adapts web audio recorder functionality to React Native using expo-audio-stream
 */

import { ExpoPlayAudioStream } from '@cjblack/expo-audio-stream';
import type { AudioDataEvent } from '@cjblack/expo-audio-stream';
import { Audio } from 'expo-av';

export interface AudioRecorderConfig {
  sampleRate: number;
  channels: number;
  bitsPerSample: number;
  onAudioData: (pcmData: ArrayBuffer) => void;
}

class AudioRecorderService {
  private isRecording: boolean = false;
  private config: AudioRecorderConfig | null = null;
  private subscription: any = null;

  /**
   * Initialize and start audio recording
   * @param config Audio configuration matching server requirements (16kHz, mono, 16-bit PCM)
   */
  async startRecording(config: AudioRecorderConfig): Promise<void> {
    if (this.isRecording) {
      console.warn('AudioRecorderService: Already recording');
      return;
    }

    this.config = config;

    try {
      // Request microphone permissions
      const { granted } = await Audio.requestPermissionsAsync();

      if (!granted) {
        throw new Error('Microphone permission not granted');
      }

      // Configure audio mode
      await Audio.setAudioModeAsync({
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
        allowsRecordingIOS: true,
      });

      // Start recording with expo-audio-stream
      const { recordingResult, subscription } = await ExpoPlayAudioStream.startRecording({
        sampleRate: 16000 as 16000 | 44100 | 48000,
        channels: config.channels as 1 | 2,
        encoding: 'pcm_16bit',
        interval: 100, // Send data every 100ms
        onAudioStream: async (audioData: AudioDataEvent) => {
          // audioData contains PCM samples
          const pcmBuffer = this.convertToPCMBuffer(audioData);
          if (pcmBuffer && config.onAudioData) {
            config.onAudioData(pcmBuffer);
          }
        },
      });

      this.subscription = subscription || null;
      this.isRecording = true;

      console.log('AudioRecorderService: Recording started', {
        sampleRate: config.sampleRate,
        channels: config.channels,
        bitsPerSample: config.bitsPerSample,
        recordingResult,
      });
    } catch (error) {
      console.error('AudioRecorderService: Failed to start recording', error);
      throw error;
    }
  }

  /**
   * Stop audio recording
   */
  async stopRecording(): Promise<void> {
    if (!this.isRecording) {
      console.warn('AudioRecorderService: Not currently recording');
      return;
    }

    try {
      // Unsubscribe from audio events
      if (this.subscription && this.subscription.remove) {
        this.subscription.remove();
        this.subscription = null;
      }

      // Stop recording
      await ExpoPlayAudioStream.stopRecording();

      this.isRecording = false;
      this.config = null;

      console.log('AudioRecorderService: Recording stopped');
    } catch (error) {
      console.error('AudioRecorderService: Failed to stop recording', error);
      throw error;
    }
  }

  /**
   * Convert audio data to PCM buffer
   * @param audioData Audio data from expo-audio-stream
   * @returns ArrayBuffer containing 16-bit PCM samples
   */
  private convertToPCMBuffer(audioData: AudioDataEvent): ArrayBuffer | null {
    try {
      // expo-audio-stream provides data in AudioDataEvent format
      if (audioData.data) {
        // If data is already a buffer
        if (audioData.data instanceof ArrayBuffer) {
          return audioData.data;
        }

        // If data is base64 string
        if (typeof audioData.data === 'string') {
          return this.base64ToArrayBuffer(audioData.data);
        }

        // If data is an array of numbers
        if (Array.isArray(audioData.data)) {
          const int16Array = new Int16Array(audioData.data);
          return int16Array.buffer;
        }
      }

      // Fallback: try to extract samples directly
      if ((audioData as any).samples) {
        const int16Array = new Int16Array((audioData as any).samples);
        return int16Array.buffer;
      }

      console.warn('AudioRecorderService: Unknown audio data format', audioData);
      return null;
    } catch (error) {
      console.error('AudioRecorderService: Failed to convert audio data', error);
      return null;
    }
  }

  /**
   * Convert base64 string to ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    // Remove data URL prefix if present
    const base64Data = base64.replace(/^data:audio\/[a-z]+;base64,/, '');

    // Decode base64 to binary string
    const binaryString = atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);

    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    return bytes.buffer;
  }

  /**
   * Check if currently recording
   */
  isCurrentlyRecording(): boolean {
    return this.isRecording;
  }

  /**
   * Get current recording status
   */
  async getStatus(): Promise<{ isRecording: boolean; canRecord: boolean }> {
    const { granted } = await Audio.getPermissionsAsync();
    return {
      isRecording: this.isRecording,
      canRecord: granted,
    };
  }
}

// Export singleton instance
export const audioRecorderService = new AudioRecorderService();

/**
 * Helper function to start audio recording with default config
 * Matches the web implementation's 16kHz, mono, 16-bit PCM format
 */
export async function startAudioRecorder(
  onAudioData: (pcmData: ArrayBuffer) => void
): Promise<void> {
  await audioRecorderService.startRecording({
    sampleRate: 16000, // 16kHz as required by server
    channels: 1, // Mono
    bitsPerSample: 16, // 16-bit PCM
    onAudioData,
  });
}

/**
 * Helper function to stop audio recording
 */
export async function stopAudioRecorder(): Promise<void> {
  await audioRecorderService.stopRecording();
}
