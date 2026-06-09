import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAppState } from '../../_state-controller/state-controller';

const NoteTakingTimer: React.FC = () => {
  const { focusTimer, setFocusTimer, focusSessionMetadata, setCurrentRoute, disconnectVoiceChat } = useAppState();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const formatTime = (value: number) => value.toString().padStart(2, '0');

  const getTruncatedTitle = () => {
    const bookName = focusSessionMetadata?.bookName || 'Unknown Book';
    if (bookName.length > 10) {
      return `${bookName.substring(0, 10)}... - Notes`;
    }
    return `${bookName} - Notes`;
  };

  const handleBackPress = () => {
    disconnectVoiceChat().finally(() => {
      setCurrentRoute(4); // Navigate back to MonkMode
    });
  };

  // Continue the countdown if session is running
  useEffect(() => {
    const isRunning = focusSessionMetadata?.isRunning ?? false;

    if (isRunning && focusTimer) {
      intervalRef.current = setInterval(() => {
        setFocusTimer((prevTimer: { hours: number; minutes: number; seconds: number } | null) => {
          if (!prevTimer) return null;

          let { hours, minutes, seconds } = prevTimer;

          if (seconds > 0) {
            seconds -= 1;
          } else {
            if (minutes > 0) {
              minutes -= 1;
              seconds = 59;
            } else {
              if (hours > 0) {
                hours -= 1;
                minutes = 59;
                seconds = 59;
              } else {
                // Timer reached 0
                return { hours: 0, minutes: 0, seconds: 0 };
              }
            }
          }

          return { hours, minutes, seconds };
        });
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [focusSessionMetadata, focusTimer, setFocusTimer]);

  return (
    <View style={styles.container}>
      {/* Back Button */}
      <TouchableOpacity style={styles.backButton} onPress={handleBackPress}>
        <Ionicons name="arrow-back" size={24} color="#333" />
      </TouchableOpacity>

      {/* Timer Display and Title */}
      <View style={styles.centerContainer}>
        <View style={styles.timerRow}>
          <Text style={styles.timerText}>
            {focusTimer
              ? `${formatTime(focusTimer.hours)}:${formatTime(focusTimer.minutes)}:${formatTime(focusTimer.seconds)}`
              : '00:00:00'}
          </Text>
          {/* Active Session Indicator - next to timer */}
          <View style={styles.activeIndicator} />
        </View>
        <View style={styles.titleContainer}>
          <Text style={styles.titleText}>{getTruncatedTitle()}</Text>
        </View>
      </View>

      {/* Empty space for balance */}
      <View style={styles.rightSpacer} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
  },
  timerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  timerText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    letterSpacing: 1,
  },
  titleContainer: {
    backgroundColor: '#e8e8e8',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 8,
  },
  titleText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  rightSpacer: {
    width: 40,
  },
  activeIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#ff3b30',
  },
});

export default NoteTakingTimer;
