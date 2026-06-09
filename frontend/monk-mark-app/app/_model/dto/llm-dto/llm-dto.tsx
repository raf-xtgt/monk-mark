/**
 * Message model for WebSocket communication
 * Represents messages exchanged between client and server
 */

// Message metadata
export interface MessageMetadata {
    role: 'user' | 'assistant';
    message_start?: boolean;
    message_stop?: boolean;
    stop_reason?: string;
    message_type?: 'transcription' | 'response';
}

// Base message interface
export interface Message {
    type: 'text' | 'audio' | 'status' | 'error' | 'control';
    timestamp: string; // ISO 8601 datetime string
    content?: string; // Text content (for text messages)
    is_final?: boolean; // Whether this is the final version of the message
    metadata?: MessageMetadata;
}

// Text message (most common type)
export interface TextMessage extends Message {
    type: 'text';
    content: string;
    is_final: boolean;
    metadata: MessageMetadata;
}

// Audio message
export interface AudioMessage extends Message {
    type: 'audio';
    data: string; // base64-encoded audio data
    format: 'pcm';
    sample_rate: number;
    metadata: MessageMetadata;
}

// Status message
export interface StatusMessage extends Message {
    type: 'status';
    status: 'connected' | 'completed' | 'processing';
    message: string;
}

// Error message
export interface ErrorMessage extends Message {
    type: 'error';
    error_code: string;
    message: string;
    details?: string;
    recoverable: boolean;
}

// Control message
export interface ControlMessage extends Message {
    type: 'control';
    action: 'end_speech' | 'cancel' | 'ping';
}

// Union type for all message types
export type MessageEvent = TextMessage | AudioMessage | StatusMessage | ErrorMessage | ControlMessage;

// Transcript message for UI display
export interface TranscriptMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

// WebSocket connection state
export type WebSocketState = 'disconnected' | 'connecting' | 'connected' | 'error';

// Server message types (for incoming messages)
export type ServerMessage = AudioMessage | TextMessage | StatusMessage | ErrorMessage;

// Audio response message
export interface AudioResponseMessage extends AudioMessage {
    type: 'audio';
}

// Text response message
export interface TextResponseMessage extends TextMessage {
    type: 'text';
}
