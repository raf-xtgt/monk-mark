import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { TranscriptMessage } from '../../../_model/dto/llm-dto';

interface NotebookVoiceChatTranscriptDrawerProps {
  visible: boolean;
  onClose: () => void;
  transcript: TranscriptMessage[];
  currentAssistantMessage?: string;
  renderFloatingPanel?: () => React.ReactNode;
}

const NotebookVoiceChatTranscriptDrawer: React.FC<NotebookVoiceChatTranscriptDrawerProps> = ({
  visible,
  onClose,
  transcript,
  currentAssistantMessage = '',
  renderFloatingPanel,
}) => {
  const scrollViewRef = useRef<ScrollView>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (visible && scrollViewRef.current) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [transcript, currentAssistantMessage, visible]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Sort transcript by timestamp in ascending order
  const sortedTranscript = [...transcript].sort((a, b) => 
    a.timestamp.getTime() - b.timestamp.getTime()
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <TouchableOpacity
          style={styles.backdrop}
          activeOpacity={1}
          onPress={onClose}
        />
        <View style={styles.drawerContainer}>
          {/* Handle bar */}
          <View style={styles.handleBar} />

          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Chat Transcript</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          </View>

          {/* Transcript content */}
          <ScrollView
            ref={scrollViewRef}
            style={styles.transcriptScroll}
            contentContainerStyle={styles.transcriptContent}
          >
            {transcript.length === 0 ? (
              <View style={styles.emptyState}>
                <Ionicons name="chatbubbles-outline" size={48} color="#CCC" />
                <Text style={styles.emptyStateText}>
                  No messages yet. Press and hold the microphone to start chatting!
                </Text>
              </View>
            ) : (
              <>
                {sortedTranscript.map((message) => (
                  <View
                    key={message.id}
                    style={[
                      styles.messageContainer,
                      message.role === 'user'
                        ? styles.userMessage
                        : styles.assistantMessage,
                    ]}
                  >
                    <View style={styles.messageHeader}>
                      <Text style={styles.messageRole}>
                        {message.role === 'user' ? 'You' : 'AI Tutor'}
                      </Text>
                      <Text style={styles.messageTime}>
                        {formatTime(message.timestamp)}
                      </Text>
                    </View>
                    <Text style={styles.messageContent}>{message.content}</Text>
                  </View>
                ))}

                {/* Show current assistant message being typed */}
                {currentAssistantMessage && (
                  <View
                    style={[styles.messageContainer, styles.assistantMessage]}
                  >
                    <View style={styles.messageHeader}>
                      <Text style={styles.messageRole}>AI Tutor</Text>
                      <ActivityIndicator size="small" color="#666" />
                    </View>
                    <Text style={styles.messageContent}>
                      {currentAssistantMessage}
                    </Text>
                  </View>
                )}
              </>
            )}
          </ScrollView>
        </View>

        {/* Floating panel on top of drawer */}
        {renderFloatingPanel && (
          <View style={styles.floatingPanelContainer}>
            {renderFloatingPanel()}
          </View>
        )}
      </View>
    </Modal>
  );
};

const { height } = Dimensions.get('window');

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  floatingPanelContainer: {
    position: 'absolute',
    bottom: 20,
    right: 16,
    zIndex: 999,
    elevation: 20,
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  drawerContainer: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    height: height * 0.7,
    paddingBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 10,
  },
  handleBar: {
    width: 40,
    height: 4,
    backgroundColor: '#DDD',
    borderRadius: 2,
    alignSelf: 'center',
    marginTop: 12,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#EEE',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  transcriptScroll: {
    flex: 1,
    minHeight: 200,
  },
  transcriptContent: {
    padding: 16,
    paddingBottom: 32,
  },
  messageContainer: {
    padding: 12,
    borderRadius: 12,
    marginBottom: 8,
  },
  userMessage: {
    backgroundColor: '#E3F2FD',
    alignSelf: 'flex-end',
    maxWidth: '80%',
  },
  assistantMessage: {
    backgroundColor: '#F5F5F5',
    alignSelf: 'flex-start',
    maxWidth: '80%',
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  messageRole: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  messageTime: {
    fontSize: 11,
    color: '#999',
  },
  messageContent: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyStateText: {
    marginTop: 16,
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
});

export default NotebookVoiceChatTranscriptDrawer;
