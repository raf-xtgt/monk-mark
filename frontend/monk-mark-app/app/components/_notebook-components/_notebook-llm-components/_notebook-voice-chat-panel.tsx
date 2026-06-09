import React from 'react';
import { View, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NotebookVoiceChatPanelProps {
  onDocumentPress: () => void;
  onMicrophonePressIn: () => void;
  onMicrophonePressOut: () => void;
  isRecording: boolean;
  isConnected: boolean;
}

const NotebookVoiceChatPanel: React.FC<NotebookVoiceChatPanelProps> = ({
  onDocumentPress,
  onMicrophonePressIn,
  onMicrophonePressOut,
  isRecording,
  isConnected,
}) => {
  const pulseAnim = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    if (isRecording) {
      // Start pulsing animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      // Stop animation
      pulseAnim.setValue(1);
    }
  }, [isRecording]);

  const handleMicButtonPress = () => {
    if (isRecording) {
      onMicrophonePressOut();
    } else {
      onMicrophonePressIn();
    }
  };

  return (
    <View style={styles.container}>
      {/* microphone/stop button - tap to toggle */}
      <TouchableOpacity
        style={[
          styles.iconButton,
          isRecording && styles.activeButton,
          !isConnected && styles.disconnectedButton,
        ]}
        onPress={handleMicButtonPress}
        activeOpacity={0.7}
        disabled={!isConnected}
      >
        <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
          <Ionicons
            name={isRecording ? 'stop' : 'mic-outline'}
            size={24}
            color="#FFFFFF"
          />
        </Animated.View>
      </TouchableOpacity>

      {/* chat transcript button */}
      <TouchableOpacity
        style={styles.iconButton}
        onPress={onDocumentPress}
        activeOpacity={0.7}
      >
        <Ionicons name="document-text" size={24} color="#FFFFFF" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#2196F3',
    borderRadius: 30,
    paddingVertical: 8,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  iconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  activeButton: {
    backgroundColor: 'rgba(255, 0, 0, 0.3)',
  },
  disconnectedButton: {
    backgroundColor: 'rgba(128, 128, 128, 0.3)',
    opacity: 0.5,
  },
});

export default NotebookVoiceChatPanel;
