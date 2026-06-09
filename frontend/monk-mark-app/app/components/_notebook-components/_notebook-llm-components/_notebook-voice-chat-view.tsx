import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import NotebookVoiceChatPanel from './_notebook-voice-chat-panel';
import NotebookVoiceChatTranscriptDrawer from './_notebook-voice-chat-transcript-drawer';
import {
  TranscriptMessage,
  ServerMessage,
  AudioResponseMessage,
  TextResponseMessage,
  StatusMessage,
  ErrorMessage,
  WebSocketState
} from '../../../_model/dto/llm-dto';
import { WS_TUTOR_URL } from '../../../_constants/api-constants';
import {
  startAudioRecorder,
  stopAudioRecorder,
} from '../../../_services/_audio/_audio-recorder-service';
import {
  initializeAudioPlayer,
  playAudioData,
  stopAudioPlayback,
  startNewPlaybackTurn,
} from '../../../_services/_audio/_audio-player-service';
import { useAppState } from '../../../_state-controller/state-controller';
import { NotebookLlmChatTranscriptService } from '../../../_services/_notebook-llm-chat-transcript-service';

const NotebookVoiceChatView: React.FC = () => {
  const { user, focusSession, currentNotebookGuid, notebookLlmChatGuid, notebookChatTranscript, setNotebookChatTranscript, setNotebookLlmChatGuid, registerVoiceChatCleanup } = useAppState();

  const [isDrawerVisible, setIsDrawerVisible] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<WebSocketState>('disconnected');
  const [currentAssistantMessage, setCurrentAssistantMessage] = useState<string>('');

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const currentUserMessageIdRef = useRef<string | null>(null);
  const currentUserMessageTimestampRef = useRef<string | null>(null);
  const currentUserMessageContentRef = useRef<string>('');
  const currentAssistantMessageIdRef = useRef<string | null>(null);
  const currentAssistantMessageTimestampRef = useRef<string | null>(null);
  const chatHdrGuidRef = useRef<string | null>(null);

  useEffect(() => {
    // Initialize audio player on mount
    initializeAudioPlayer().catch((error) => {
      console.error('Failed to initialize audio player:', error);
    });

    // Load existing chat transcript if available
    loadExistingTranscript();

    // Register cleanup function so sibling components can trigger disconnect
    registerVoiceChatCleanup(cleanup);

    // Cleanup on unmount
    return () => {
      registerVoiceChatCleanup(null);
      cleanup();
    };
  }, [currentNotebookGuid]);

  /**
   * Load existing chat transcript from database
   */
  const loadExistingTranscript = async () => {
    if (!currentNotebookGuid || !user?.guid) {
      console.warn('No notebook GUID or user GUID available');
      // Still establish WebSocket connection
      connectWebSocket();
      return;
    }

    try {
      const response = await NotebookLlmChatTranscriptService.getByNotebookHdr({
        notebook_hdr_guid: currentNotebookGuid,
        user_guid: user.guid,
        library_hdr_guid: focusSession?.libraryHdrGuid,
      });

      if (response) {
        // Store the chat header GUID from the response
        if (response.chat_hdr_guid) {
          setNotebookLlmChatGuid(response.chat_hdr_guid);
          chatHdrGuidRef.current = response.chat_hdr_guid; // Store in ref for immediate access
        }

        // Convert database records to TranscriptMessage format
        if (response.chat_transcripts && response.chat_transcripts.length > 0) {
          const messages: TranscriptMessage[] = response.chat_transcripts.map((record: any) => ({
            id: record.guid,
            role: record.sender === 'user' ? 'user' : 'assistant',
            content: record.msg_content,
            timestamp: new Date(record.created_date),
          }));

          // Update state with loaded messages
          setNotebookChatTranscript(messages);

          console.log(`Loaded ${messages.length} existing messages`);
        }
      }
    } catch (error) {
      console.error('Failed to load existing transcript:', error);
    } finally {
      // Establish WebSocket connection after loading transcript
      connectWebSocket();
    }
  };

  /**
   * Save message to database
   */
  const saveMessageToDatabase = async (message: TranscriptMessage) => {
    if (!user?.guid) {
      console.error('No user GUID available');
      return;
    }

    try {
      // Use ref value for immediate access, fallback to state
      const chatHdrGuid = chatHdrGuidRef.current || notebookLlmChatGuid;
      console.log("chatHdrGuid", chatHdrGuid)

      if (!chatHdrGuid) {
        console.error('Failed to get or create chat header');
        return;
      }

      // Save message to database
      await NotebookLlmChatTranscriptService.create({
        user_guid: user.guid,
        llm_chat_hdr_guid: chatHdrGuid,
        msg_content: message.content,
        sender: message.role,
      });

      console.log('Message saved to database:', message.id);
    } catch (error) {
      console.error('Failed to save message to database:', error);
    }
  };

  /**
   * Build WebSocket URL with agent context query parameters.
   * Appends user_guid, library_hdr_guid, notebook_hdr_guid, and
   * llm_chat_hdr_guid so the backend can inject them into ADK Session State.
   */
  const buildWebSocketUrl = (): string => {
    const params = new URLSearchParams();

    if (user?.guid) {
      params.append('user_guid', user.guid);
    }
    if (focusSession?.libraryHdrGuid) {
      params.append('library_hdr_guid', focusSession.libraryHdrGuid);
    }
    if (currentNotebookGuid) {
      params.append('notebook_hdr_guid', currentNotebookGuid);
    }
    // Use ref for immediate access (may be set during loadExistingTranscript)
    const chatGuid = chatHdrGuidRef.current || notebookLlmChatGuid;
    if (chatGuid) {
      params.append('llm_chat_hdr_guid', chatGuid);
    }
    if (focusSession?.focusSessionGuid) {
      params.append('focus_session_guid', focusSession.focusSessionGuid);
    }

    const queryString = params.toString();
    return queryString ? `${WS_TUTOR_URL}?${queryString}` : WS_TUTOR_URL;
  };

  /**
   * Establish WebSocket connection
   */
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      setConnectionState('connecting');
      const wsUrl = buildWebSocketUrl();
      console.log('Connecting to WebSocket:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionState('connected');
        setIsConnected(true);

        // Clear any pending reconnect
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        handleWebSocketMessage(event.data);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionState('error');
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setConnectionState('disconnected');
        setIsConnected(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionState('error');
      setIsConnected(false);
    }
  };

  /**
   * Handle incoming WebSocket messages
   */
  const handleWebSocketMessage = (data: string) => {
    try {
      const message: ServerMessage = JSON.parse(data);

      switch (message.type) {
        case 'audio':
          handleAudioResponse(message as AudioResponseMessage);
          break;
        case 'text':
          handleTextResponse(message as TextResponseMessage);
          break;
        case 'status':
          handleStatusMessage(message as StatusMessage);
          break;
        case 'error':
          handleErrorMessage(message as ErrorMessage);
          break;
        default:
          console.warn('Unknown message type:', message);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  /**
   * Handle audio response from server
   */
  const handleAudioResponse = async (message: AudioResponseMessage) => {
    try {
      // Handle message start metadata - start a new playback turn BEFORE
      // playing the first chunk so all chunks in this turn share the same
      // turn ID and are queued sequentially instead of overlapping.
      if (message.metadata?.message_start) {
        startNewPlaybackTurn();
        currentAssistantMessageIdRef.current = generateMessageId();
        currentAssistantMessageTimestampRef.current = message.timestamp;
        setCurrentAssistantMessage('');
      }

      // Decode base64 audio data
      const audioData = base64ToArrayBuffer(message.data);

      // Play audio
      await playAudioData(audioData);

      // Note: Audio messages are typically not added to transcript as text
      // Only text transcriptions are added via handleTextResponse
    } catch (error) {
      console.error('Failed to handle audio response:', error);
    }
  };

  /**
   * Handle text response from server
   */
  const handleTextResponse = async (message: TextResponseMessage) => {
    try {
      // Check if this is a user transcription message
      const isUserTranscription = message.metadata?.role === 'user';

      if (isUserTranscription) {
        // Handle user's transcribed speech
        if (message.is_final) {
          // Final transcription - store it and update the existing user message in transcript
          currentUserMessageContentRef.current = message.content;

          // Mutate the last user message in transcript to replace "[Voice message]"
          // with the actual transcribed content for immediate UI feedback.
          if (message.content) {
            setNotebookChatTranscript((prev) => {
              // Find the last user message (most recent one we added)
              const lastUserIdx = [...prev].reverse().findIndex((m) => m.role === 'user');
              if (lastUserIdx === -1) return prev;

              const actualIdx = prev.length - 1 - lastUserIdx;
              const target = prev[actualIdx];

              // Only update if it's still a placeholder or partial transcription
              if (target.content === '[Voice message]' || target.content !== message.content) {
                const updated = [...prev];
                updated[actualIdx] = { ...target, content: message.content };
                return updated;
              }
              return prev;
            });
          }
        } else {
          // Partial transcription - update accumulator and live-update the user bubble
          currentUserMessageContentRef.current = message.content;

          if (message.content) {
            setNotebookChatTranscript((prev) => {
              const lastUserIdx = [...prev].reverse().findIndex((m) => m.role === 'user');
              if (lastUserIdx === -1) return prev;

              const actualIdx = prev.length - 1 - lastUserIdx;
              const target = prev[actualIdx];

              if (target.content === '[Voice message]' || target.content !== message.content) {
                const updated = [...prev];
                updated[actualIdx] = { ...target, content: message.content };
                return updated;
              }
              return prev;
            });
          }
        }
        return;
      }

      // Handle assistant message
      if (message.metadata?.message_start) {
        currentAssistantMessageIdRef.current = generateMessageId();
        currentAssistantMessageTimestampRef.current = message.timestamp;
        setCurrentAssistantMessage('');
      }

      // For final messages, add directly to transcript
      if (message.is_final && message.content) {
        const newMessage: TranscriptMessage = {
          id: currentAssistantMessageIdRef.current || generateMessageId(),
          role: 'assistant',
          content: message.content,
          timestamp: currentAssistantMessageTimestampRef.current
            ? new Date(currentAssistantMessageTimestampRef.current)
            : new Date(),
        };

        // Add to transcript
        setNotebookChatTranscript((prev) => [...prev, newMessage]);

        // Save to database — handled server-side by save_conversation_turn tool
        // await saveMessageToDatabase(newMessage);

        // Reset for next message
        currentAssistantMessageIdRef.current = null;
        currentAssistantMessageTimestampRef.current = null;
        setCurrentAssistantMessage('');
      } else if (!message.is_final) {
        // Partial text - show in current message for streaming effect
        setCurrentAssistantMessage((prev) => prev + message.content);
      }
    } catch (error) {
      console.error('Failed to handle text response:', error);
    }
  };

  /**
   * Reload transcripts from the database to refresh messages
   * (replaces "[Voice message]" placeholders with actual transcribed text).
   * Merges DB data with any in-flight local messages to avoid losing
   * messages from a turn that is currently in progress.
   */
  const reloadTranscripts = async () => {
    if (!currentNotebookGuid || !user?.guid) {
      return;
    }

    try {
      const response = await NotebookLlmChatTranscriptService.getByNotebookHdr({
        notebook_hdr_guid: currentNotebookGuid,
        user_guid: user.guid,
        library_hdr_guid: focusSession?.libraryHdrGuid,
      });

      if (response) {
        // Update chat header GUID if returned
        if (response.chat_hdr_guid) {
          setNotebookLlmChatGuid(response.chat_hdr_guid);
          chatHdrGuidRef.current = response.chat_hdr_guid;
        }

        if (response.chat_transcripts && response.chat_transcripts.length > 0) {
          const dbMessages: TranscriptMessage[] = response.chat_transcripts.map((record: any) => ({
            id: record.guid,
            role: record.sender === 'user' ? 'user' : 'assistant',
            content: record.msg_content,
            timestamp: new Date(record.created_date),
          }));

          // Merge strategy: use DB messages as the base, then append any
          // local-only messages that are newer than the latest DB message.
          // This preserves in-flight messages from a turn currently in progress.
          setNotebookChatTranscript((prev) => {
            const latestDbTimestamp = dbMessages.length > 0
              ? Math.max(...dbMessages.map(m => m.timestamp.getTime()))
              : 0;

            // Keep local messages that are newer than the latest DB record
            // and don't have a matching ID in the DB set (i.e., not yet persisted).
            const dbIds = new Set(dbMessages.map(m => m.id));
            const localOnlyMessages = prev.filter(
              (m) => !dbIds.has(m.id) && m.timestamp.getTime() > latestDbTimestamp
            );

            if (localOnlyMessages.length > 0) {
              console.log(`Preserving ${localOnlyMessages.length} in-flight local messages during reload`);
              return [...dbMessages, ...localOnlyMessages];
            }

            return dbMessages;
          });

          console.log(`Reloaded ${dbMessages.length} messages from database`);
        }
      }
    } catch (error) {
      console.error('Failed to reload transcripts:', error);
    }
  };

  /**
   * Handle status message from server
   */
  const handleStatusMessage = (message: StatusMessage) => {
    console.log('Status:', message.status, message.message);

    if (message.status === 'completed') {
      // Turn complete - clear any partial message display
      setCurrentAssistantMessage('');
      currentAssistantMessageIdRef.current = null;
      currentAssistantMessageTimestampRef.current = null;

      // Reload transcripts from DB to replace "[Voice message]" placeholders
      // with the actual transcribed user input saved by the backend agent.
      // Add a short delay to allow the backend fallback persistence to complete
      // before fetching updated data from the database.
      setTimeout(() => {
        reloadTranscripts();
      }, 1500);
    }
  };

  /**
   * Handle error message from server
   */
  const handleErrorMessage = (message: ErrorMessage) => {
    console.error('Server error:', message.error_code, message.message);

    Alert.alert(
      'Error',
      message.message,
      [{ text: 'OK' }]
    );

    if (!message.recoverable) {
      // Stop recording on unrecoverable error
      handleMicrophonePressOut();
    }
  };

  /**
   * Handle microphone press (start recording)
   */
  const handleMicrophonePressIn = async () => {
    if (!isConnected) {
      Alert.alert('Not Connected', 'Please wait for connection to establish');
      return;
    }

    if (isRecording) {
      console.warn('Already recording');
      return;
    }

    try {
      // Start recording and send audio data via WebSocket
      await startAudioRecorder((pcmData: ArrayBuffer) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          // Send audio data as binary
          wsRef.current.send(pcmData);
        }
      });

      setIsRecording(true);

      // Create user message placeholder with current timestamp
      currentUserMessageIdRef.current = generateMessageId();
      currentUserMessageTimestampRef.current = new Date().toISOString();
      currentUserMessageContentRef.current = ''; // Reset transcription content

      console.log('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Recording Error', 'Failed to start recording. Please check microphone permissions.');
    }
  };

  /**
   * Handle microphone release (stop recording)
   */
  const handleMicrophonePressOut = async () => {
    if (!isRecording) {
      return;
    }

    try {
      // Stop recording
      await stopAudioRecorder();
      setIsRecording(false);

      // Send end_speech control message
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'control',
          action: 'end_speech'
        }));
      }

      // Finalize user message
      if (currentUserMessageIdRef.current) {
        console.log("currentUserMessageIdRef", currentUserMessageIdRef)

        const userMessage: TranscriptMessage = {
          id: currentUserMessageIdRef.current,
          role: 'user',
          content: currentUserMessageContentRef.current || '[Voice message]', // Use transcription if available
          timestamp: currentUserMessageTimestampRef.current
            ? new Date(currentUserMessageTimestampRef.current)
            : new Date(),
        };

        setNotebookChatTranscript((prev) => [...prev, userMessage]);

        // Save to database — handled server-side by save_conversation_turn tool
        // await saveMessageToDatabase(userMessage);

        currentUserMessageIdRef.current = null;
        currentUserMessageTimestampRef.current = null;
        currentUserMessageContentRef.current = '';
      }

      console.log('Recording stopped');
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  };

  /**
   * Handle document/transcript button press
   */
  const handleDocumentPress = () => {
    setIsDrawerVisible(true);
  };

  /**
   * Handle drawer close
   */
  const handleCloseDrawer = () => {
    setIsDrawerVisible(false);
  };

  /**
   * Cleanup resources
   */
  const cleanup = async () => {
    // Stop recording if active
    if (isRecording) {
      await stopAudioRecorder();
    }

    // Stop audio playback
    await stopAudioPlayback();

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  };

  /**
   * Convert base64 string to ArrayBuffer
   */
  const base64ToArrayBuffer = (base64: string): ArrayBuffer => {
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
  };

  /**
   * Generate unique message ID
   */
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  };

  return (
    <View style={styles.container}>
      <NotebookVoiceChatPanel
        onDocumentPress={handleDocumentPress}
        onMicrophonePressIn={handleMicrophonePressIn}
        onMicrophonePressOut={handleMicrophonePressOut}
        isRecording={isRecording}
        isConnected={isConnected}
      />
      <NotebookVoiceChatTranscriptDrawer
        visible={isDrawerVisible}
        onClose={handleCloseDrawer}
        transcript={notebookChatTranscript}
        currentAssistantMessage={currentAssistantMessage}
        renderFloatingPanel={() => (
          <NotebookVoiceChatPanel
            onDocumentPress={handleCloseDrawer}
            onMicrophonePressIn={handleMicrophonePressIn}
            onMicrophonePressOut={handleMicrophonePressOut}
            isRecording={isRecording}
            isConnected={isConnected}
          />
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 20,
    right: 16,
    zIndex: 100,
  },
});

export default NotebookVoiceChatView;
