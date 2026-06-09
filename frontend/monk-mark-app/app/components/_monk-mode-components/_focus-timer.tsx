import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import { useAppState } from '../../_state-controller/state-controller';

const MIN_MINUTES = 30;
const MAX_HOURS = 5;

interface FocusTimerProps {
  isRunning: boolean;
  onTimeUpdate?: (hours: number, minutes: number, seconds: number) => void;
}

const FocusTimer: React.FC<FocusTimerProps> = ({ isRunning, onTimeUpdate }) => {
  const { focusTimer, setFocusTimer, focusSessionMetadata, setFocusSessionMetadata } = useAppState();
  const [showModal, setShowModal] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Initialize from global state or defaults
  const [hours, setHours] = useState(focusTimer?.hours ?? 0);
  const [minutes, setMinutes] = useState(focusTimer?.minutes ?? 30);
  const [seconds, setSeconds] = useState(focusTimer?.seconds ?? 0);

  // Sync local state with global state when component mounts or global state changes
  useEffect(() => {
    if (focusTimer) {
      setHours(focusTimer.hours);
      setMinutes(focusTimer.minutes);
      setSeconds(focusTimer.seconds);
    }
  }, [focusTimer]);

  useEffect(() => {
    const shouldRun = focusSessionMetadata?.isRunning ?? isRunning;
    
    if (shouldRun) {
      intervalRef.current = setInterval(() => {
        setSeconds((prevSeconds) => {
          if (prevSeconds > 0) {
            return prevSeconds - 1;
          } else {
            setMinutes((prevMinutes) => {
              if (prevMinutes > 0) {
                return prevMinutes - 1;
              } else {
                setHours((prevHours) => {
                  if (prevHours > 0) {
                    setMinutes(59);
                    return prevHours - 1;
                  }
                  return 0;
                });
                return 59;
              }
            });
            return 59;
          }
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
  }, [isRunning, focusSessionMetadata]);

  useEffect(() => {
    // Sync with global state
    setFocusTimer({ hours, minutes, seconds });
    
    if (onTimeUpdate) {
      onTimeUpdate(hours, minutes, seconds);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hours, minutes, seconds]);

  const incrementHours = () => {
    if (hours < MAX_HOURS) {
      setHours(hours + 1);
    }
  };

  const decrementHours = () => {
    if (hours > 0) {
      setHours(hours - 1);
    } else if (minutes < MIN_MINUTES) {
      setMinutes(MIN_MINUTES);
    }
  };

  const incrementMinutes = () => {
    if (minutes < 59) {
      setMinutes(minutes + 1);
    } else if (hours < MAX_HOURS) {
      setMinutes(0);
      setHours(hours + 1);
    }
  };

  const decrementMinutes = () => {
    if (minutes > 0) {
      setMinutes(minutes - 1);
    } else if (hours > 0) {
      setMinutes(59);
      setHours(hours - 1);
    }

    // Ensure minimum 30 minutes
    if (hours === 0 && minutes <= MIN_MINUTES) {
      setMinutes(MIN_MINUTES);
    }
  };

  const incrementSeconds = () => {
    if (seconds < 59) {
      setSeconds(seconds + 1);
    } else {
      setSeconds(0);
      incrementMinutes();
    }
  };

  const decrementSeconds = () => {
    if (seconds > 0) {
      setSeconds(seconds - 1);
    } else if (minutes > 0 || hours > 0) {
      setSeconds(59);
      decrementMinutes();
    }
  };

  const formatTime = (value: number) => value.toString().padStart(2, '0');

  const isValidTime = () => {
    const totalMinutes = hours * 60 + minutes;
    return totalMinutes >= MIN_MINUTES && hours <= MAX_HOURS;
  };

  return (
    <View style={styles.container}>


      {/* Time Display */}
      <View style={styles.timeDisplay}>
        <Text style={styles.timeText}>
          {formatTime(hours)}:{formatTime(minutes)}:{formatTime(seconds)}
        </Text>
      </View>

      {/* Set Focus Time Button - Only show when timer is not running */}
      {!isRunning && (
        <TouchableOpacity
          style={styles.setTimeButton}
          onPress={() => setShowModal(true)}
        >
          <Text style={styles.setTimeButtonText}>Set Focus Time</Text>
        </TouchableOpacity>
      )}

      {/* Time Picker Modal */}
      <Modal
        visible={showModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Set Focus Time</Text>
            <Text style={styles.modalSubtitle}>
              Min: 30 minutes | Max: 5 hours
            </Text>

            <View style={styles.pickerContainer}>
              {/* Hours Picker */}
              <View style={styles.timePickerColumn}>
                <TouchableOpacity onPress={incrementHours} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▲</Text>
                </TouchableOpacity>
                <Text style={styles.pickerValue}>{formatTime(hours)}</Text>
                <TouchableOpacity onPress={decrementHours} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▼</Text>
                </TouchableOpacity>
                <Text style={styles.pickerLabel}>Hours</Text>
              </View>

              <Text style={styles.timeSeparator}>:</Text>

              {/* Minutes Picker */}
              <View style={styles.timePickerColumn}>
                <TouchableOpacity onPress={incrementMinutes} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▲</Text>
                </TouchableOpacity>
                <Text style={styles.pickerValue}>{formatTime(minutes)}</Text>
                <TouchableOpacity onPress={decrementMinutes} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▼</Text>
                </TouchableOpacity>
                <Text style={styles.pickerLabel}>Minutes</Text>
              </View>

              <Text style={styles.timeSeparator}>:</Text>

              {/* Seconds Picker */}
              <View style={styles.timePickerColumn}>
                <TouchableOpacity onPress={incrementSeconds} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▲</Text>
                </TouchableOpacity>
                <Text style={styles.pickerValue}>{formatTime(seconds)}</Text>
                <TouchableOpacity onPress={decrementSeconds} style={styles.pickerButton}>
                  <Text style={styles.pickerButtonText}>▼</Text>
                </TouchableOpacity>
                <Text style={styles.pickerLabel}>Seconds</Text>
              </View>
            </View>

            {!isValidTime() && (
              <Text style={styles.errorText}>
                Time must be between 30 minutes and 5 hours
              </Text>
            )}

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton, !isValidTime() && styles.disabledButton]}
                onPress={() => {
                  if (isValidTime()) {
                    setShowModal(false);
                  }
                }}
                disabled={!isValidTime()}
              >
                <Text style={styles.confirmButtonText}>Done</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  clockContainer: {
    width: 140,
    height: 140,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  clockCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 6,
    borderColor: '#ffffff',
    backgroundColor: '#4a4a5e',
    justifyContent: 'center',
    alignItems: 'center',
  },
  clockHand: {
    position: 'absolute',
    width: 4,
    height: 22,
    backgroundColor: '#ffffff',
    borderRadius: 2,
    top: 18,
  },
  clockMinuteHand: {
    position: 'absolute',
    width: 3,
    height: 28,
    backgroundColor: '#ffffff',
    borderRadius: 2,
    top: 12,
    transform: [{ rotate: '90deg' }],
  },
  floatingShape: {
    position: 'absolute',
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
  },
  shapeYellow: {
    borderColor: '#f4c542',
  },
  shapeCyan: {
    borderColor: '#4ecdc4',
  },
  shapePink: {
    borderColor: '#ff6b9d',
  },
  shape1: { top: 15, left: 45 },
  shape2: { top: 30, left: 15 },
  shape3: { top: 45, right: 15 },
  shape4: { top: 8, right: 30 },
  shape5: { bottom: 30, left: 22 },
  shape6: { bottom: 45, left: 60 },
  shape7: { bottom: 60, left: 8 },
  shape8: { bottom: 15, right: 22 },
  timeDisplay: {
    marginBottom: 15,
  },
  timeText: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#ffffff',
    letterSpacing: 2,
  },
  setTimeButton: {
    backgroundColor: '#e8e8e8',
    paddingHorizontal: 28,
    paddingVertical: 12,
    borderRadius: 10,
  },
  setTimeButtonText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 30,
    width: '85%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  pickerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  timePickerColumn: {
    alignItems: 'center',
  },
  pickerButton: {
    padding: 10,
  },
  pickerButtonText: {
    fontSize: 24,
    color: '#6200ee',
  },
  pickerValue: {
    fontSize: 36,
    fontWeight: 'bold',
    marginVertical: 10,
    minWidth: 60,
    textAlign: 'center',
  },
  pickerLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  timeSeparator: {
    fontSize: 36,
    fontWeight: 'bold',
    marginHorizontal: 10,
  },
  errorText: {
    color: '#ff3b30',
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 15,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#f0f0f0',
  },
  cancelButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButton: {
    backgroundColor: '#6200ee',
  },
  confirmButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  disabledButton: {
    backgroundColor: '#cccccc',
  },
});

export default FocusTimer;
