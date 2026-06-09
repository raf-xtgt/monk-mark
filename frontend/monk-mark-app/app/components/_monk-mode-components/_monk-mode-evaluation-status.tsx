import React from 'react';
import { Text, View, StyleSheet, ActivityIndicator } from 'react-native';

interface MonkModeEvaluationStatusProps {
  isEvaluating: boolean;
  statusMessage: string | null;
}

const MonkModeEvaluationStatus: React.FC<MonkModeEvaluationStatusProps> = ({
  isEvaluating,
  statusMessage,
}) => {
  if (!isEvaluating && !statusMessage) {
    return null;
  }

  return (
    <View style={styles.container}>
      {isEvaluating && <ActivityIndicator size="small" color="#4ecdc4" />}
      {statusMessage && (
        <Text style={styles.statusText}>{statusMessage}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginHorizontal: 20,
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
  },
  statusText: {
    fontSize: 13,
    color: '#ffffff',
    opacity: 0.9,
    flexShrink: 1,
    fontStyle: 'italic',
  },
});

export default MonkModeEvaluationStatus;
