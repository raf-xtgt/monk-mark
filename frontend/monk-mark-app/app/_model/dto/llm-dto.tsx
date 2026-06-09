/**
 * TypeScript interfaces for WebSocket voice tutor communication
 * Matches backend message protocol from websocket_config.py and websocket_helper.py
 */

// Message types from backend
export type WebSocketMessageType = 'audio' | 'text' | 'status' | 'error' | 'control';

// Base message structure
export interface BaseWebSocketMessage {
  type: WebSocketMessageType;
  timestamp: string; // ISO 8601 datetime string from server
}

// Client -> Server: Audio message
export interface AudioUploadMessage {
  type: 'audio';
  data: string; // base64-encoded PCM audio
  format: 'pcm';
}

// Client -> Server: Control message
export interface ControlMessage {
  type: 'control';
  action: 'end_speech' | 'cancel' | 'ping';
}

// Server -> Client: Audio response
export interface AudioResponseMessage extends BaseWebSocketMessage {
  type: 'audio';
  data: string; // base64-encoded PCM audio
  format: 'pcm';
  sample_rate: number;
  metadata?: {
    message_start?: boolean;
    message_stop?: boolean;
    stop_reason?: string;
    role?: string;
  };
}

// Server -> Client: Text response
export interface TextResponseMessage extends BaseWebSocketMessage {
  type: 'text';
  content: string;
  is_final: boolean;
  metadata?: {
    message_start?: boolean;
    message_stop?: boolean;
    stop_reason?: string;
    role?: string;
  };
}

// Server -> Client: Status message
export interface StatusMessage extends BaseWebSocketMessage {
  type: 'status';
  status: 'connected' | 'completed';
  message: string;
  metadata?: {
    stop_reason?: string;
    audio_chunks?: number;
    text_chunks?: number;
  };
}

// Server -> Client: Error message
export interface ErrorMessage extends BaseWebSocketMessage {
  type: 'error';
  error_code: string;
  message: string;
  details?: string;
  recoverable: boolean;
}

// Union type for all server messages
export type ServerMessage = 
  | AudioResponseMessage 
  | TextResponseMessage 
  | StatusMessage 
  | ErrorMessage;

// Union type for all client messages
export type ClientMessage = AudioUploadMessage | ControlMessage;

// WebSocket event handlers
export interface WebSocketEventHandlers {
  onAudioResponse?: (message: AudioResponseMessage) => void;
  onTextResponse?: (message: TextResponseMessage) => void;
  onStatus?: (message: StatusMessage) => void;
  onError?: (message: ErrorMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

// WebSocket connection state
export type WebSocketState = 'disconnected' | 'connecting' | 'connected' | 'error';

// Transcript message for UI display
export interface TranscriptMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioData?: string; // base64 audio if available
}
