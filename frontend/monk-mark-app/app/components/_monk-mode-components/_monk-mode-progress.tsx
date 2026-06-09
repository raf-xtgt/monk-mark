import React, { useMemo } from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MilestoneEvaluation } from '../../_model/dto/reward-output-dto';

interface MonkModeProgressRemarksProps {
  milestone: MilestoneEvaluation | null;
}

const TIER_NAMES = ['I', 'II', 'III', 'IV', 'V'];

const MonkModeProgressRemarks: React.FC<MonkModeProgressRemarksProps> = ({ milestone }) => {
  const tierLabel = useMemo(() => {
    if (!milestone) return '';
    const index = Math.min(milestone.next_tier - 1, TIER_NAMES.length - 1);
    return `Evolution ${TIER_NAMES[index]}`;
  }, [milestone?.next_tier]);

  if (!milestone) return null;

  // If both fulfilled, show a congratulatory state instead of remaining
  if (milestone.is_hour_fulfilled && milestone.is_note_fulfilled) {
    return (
      <View style={styles.container}>
        <View style={styles.unlockedBadge}>
          <Ionicons name="trophy" size={20} color="#f4c542" />
          <Text style={styles.unlockedText}>Milestone unlocked!</Text>
        </View>
      </View>
    );
  }

  const remainingHours = milestone.remaining_hours ?? 0;
  const remainingNotes = milestone.remaining_notes ?? 0;

  return (
    <View style={styles.container}>
      {/* Header */}
      <Text style={styles.header}>To unlock {tierLabel}</Text>

      {/* Metrics row */}
      <View style={styles.metricsRow}>
        {/* Hours metric */}
        <View style={styles.metricCard}>
          <Ionicons
            name={milestone.is_hour_fulfilled ? 'checkmark-circle' : 'time-outline'}
            size={22}
            color={milestone.is_hour_fulfilled ? '#4ecdc4' : '#ffffff'}
          />
          <Text style={[
            styles.metricValue,
            milestone.is_hour_fulfilled && styles.metricFulfilled,
          ]}>
            {milestone.is_hour_fulfilled ? 'Done' : `${remainingHours} hours`}
          </Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Notes metric */}
        <View style={styles.metricCard}>
          <Ionicons
            name={milestone.is_note_fulfilled ? 'checkmark-circle' : 'document-text-outline'}
            size={22}
            color={milestone.is_note_fulfilled ? '#f4c542' : '#ffffff'}
          />
          <Text style={[
            styles.metricValue,
            milestone.is_note_fulfilled && styles.metricFulfilled,
          ]}>
            {milestone.is_note_fulfilled ? 'Done' : `${remainingNotes} notes`}
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    alignItems: 'center',
  },
  header: {
    fontSize: 13,
    color: '#ffffff',
    opacity: 0.6,
    letterSpacing: 0.5,
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  metricsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
    gap: 20,
  },
  metricCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  metricValue: {
    fontSize: 15,
    fontWeight: '600',
    color: '#ffffff',
  },
  metricFulfilled: {
    color: '#4ecdc4',
  },
  divider: {
    width: 1,
    height: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  unlockedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: 'rgba(244, 197, 66, 0.15)',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 20,
  },
  unlockedText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#f4c542',
  },
});

export default MonkModeProgressRemarks;
