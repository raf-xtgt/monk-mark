/**
 * Audio Player Service for React Native
 * Adapts web audio player functionality to React Native using expo-audio-stream
 */

import { ExpoPlayAudioStream } from '@cjblack/expo-audio-stream';
import { Audio } from 'expo-av';

export interface AudioPlayerConfig {
  sampleRate: number;
  channels: number;
  bitsPerSample: number;
}

class AudioPlayerService {
  private config: AudioPlayerConfig | null = null;
  private currentTurnId: string = 'turn_0';
  private isInitialized: boolean = false;
  private targetSampleRate: 16000 | 44100 | 48000 = 16000;

  /**
   * Initialize audio player
   * @param config Audio configuration (24kHz, mono, 16-bit PCM from server)
   */
  async initialize(config: AudioPlayerConfig): Promise<void> {
    this.config = config;

    try {
      // Set audio mode for playback
      await Audio.setAudioModeAsync({
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      // Map the server's sample rate to a supported rate
      // expo-audio-stream only supports 16000, 44100, or 48000 Hz
      // Google ADK outputs at 24kHz, which is not directly supported
      // We'll use 48kHz (2x 24kHz) as the closest match
      if (config.sampleRate === 24000) {
        this.targetSampleRate = 48000;
        console.log('AudioPlayerService: Mapping 24kHz to 48kHz for playback');
      } else if (config.sampleRate <= 16000) {
        this.targetSampleRate = 16000;
      } else if (config.sampleRate <= 44100) {
        this.targetSampleRate = 44100;
      } else {
        this.targetSampleRate = 48000;
      }

      // Configure the sound player with the target sample rate
      await ExpoPlayAudioStream.setSoundConfig({
        sampleRate: this.targetSampleRate,
        playbackMode: 'regular',
      });

      this.isInitialized = true;
      console.log('AudioPlayerService: Initialized', {
        inputSampleRate: config.sampleRate,
        targetSampleRate: this.targetSampleRate,
      });
    } catch (error) {
      console.error('AudioPlayerService: Failed to initialize', error);
      throw error;
    }
  }

  /**
   * Start a new playback turn. Call this when the server signals a new
   * assistant message (message_start). All subsequent audio chunks will
   * be queued under this turn ID so they play back sequentially.
   */
  startNewTurn(): void {
    this.currentTurnId = `turn_${Date.now()}`;
    console.log('AudioPlayerService: New turn started', { turnId: this.currentTurnId });
  }

  /**
   * Play PCM audio data
   * @param pcmData ArrayBuffer containing 16-bit PCM samples
   */
  async playAudio(pcmData: ArrayBuffer): Promise<void> {
    if (!this.isInitialized || !this.config) {
      console.warn('AudioPlayerService: Not initialized');
      return;
    }

    try {
      // If we need to resample from 24kHz to 48kHz, we need to duplicate samples
      let audioToPlay = pcmData;

      if (this.config.sampleRate === 24000 && this.targetSampleRate === 48000) {
        audioToPlay = this.upsample24to48(pcmData);
      }

      // Convert ArrayBuffer to base64
      const base64Audio = this.arrayBufferToBase64(audioToPlay);

      // Play audio using expo-audio-stream
      // Format: pcm_s16le means signed 16-bit little-endian PCM
      // All chunks within the same turn share the same turnId so they
      // are queued and played back in order rather than overlapping.
      await ExpoPlayAudioStream.playAudio(
        base64Audio,
        this.currentTurnId,
        'pcm_s16le'
      );
    } catch (error) {
      console.error('AudioPlayerService: Failed to play audio', error);
    }
  }

  /**
   * Upsample 24kHz audio to 48kHz by duplicating each sample
   * This is a simple linear interpolation approach
   */
  private upsample24to48(input: ArrayBuffer): ArrayBuffer {
    const inputView = new Int16Array(input);
    const outputView = new Int16Array(inputView.length * 2);

    for (let i = 0; i < inputView.length; i++) {
      // Duplicate each sample to double the sample rate
      outputView[i * 2] = inputView[i];
      outputView[i * 2 + 1] = inputView[i];
    }

    return outputView.buffer;
  }

  /**
   * Convert ArrayBuffer to base64 string
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Stop audio playback
   */
  async stop(): Promise<void> {
    try {
      await ExpoPlayAudioStream.stopAudio();
      console.log('AudioPlayerService: Stopped');
    } catch (error) {
      console.error('AudioPlayerService: Failed to stop', error);
    }
  }

  /**
   * Clear audio queue for current turn
   */
  async clearQueue(): Promise<void> {
    try {
      if (this.currentTurnId) {
        await ExpoPlayAudioStream.clearPlaybackQueueByTurnId(this.currentTurnId);
      }
      console.log('AudioPlayerService: Queue cleared');
    } catch (error) {
      console.error('AudioPlayerService: Failed to clear queue', error);
    }
  }

  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    await this.stop();
    this.config = null;
    this.isInitialized = false;
    console.log('AudioPlayerService: Cleaned up');
  }
}

// Export singleton instance
export const audioPlayerService = new AudioPlayerService();

/**
 * Helper function to initialize audio player with default config
 * Matches the server's 24kHz, mono, 16-bit PCM format
 */
export async function initializeAudioPlayer(): Promise<void> {
  await audioPlayerService.initialize({
    sampleRate: 24000, // Server sends 24kHz audio
    channels: 1, // Mono
    bitsPerSample: 16, // 16-bit PCM
  });
}

/**
 * Helper function to signal a new playback turn
 */
export function startNewPlaybackTurn(): void {
  audioPlayerService.startNewTurn();
}

/**
 * Helper function to play audio data
 */
export async function playAudioData(pcmData: ArrayBuffer): Promise<void> {
  await audioPlayerService.playAudio(pcmData);
}

/**
 * Helper function to stop audio playback
 */
export async function stopAudioPlayback(): Promise<void> {
  await audioPlayerService.stop();
}
