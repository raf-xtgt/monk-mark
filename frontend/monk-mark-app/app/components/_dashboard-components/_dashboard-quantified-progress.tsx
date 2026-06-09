import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DashboardStats } from '../../_model/dto/_dashboard-dto';

interface DashboardQuantifiedProgressProps {
  stats: DashboardStats | null;
  isLoading: boolean;
}

const DashboardQuantifiedProgress: React.FC<DashboardQuantifiedProgressProps> = ({ stats, isLoading }) => {
  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text style={styles.sectionTitle}>QUANTIFIED PROGRESS</Text>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>QUANTIFIED PROGRESS</Text>
      <View style={styles.cardsRow}>
        {/* Focus Hours Card */}
        <View style={styles.card}>
          <Ionicons name="timer-outline" size={32} color="#4ECDC4" />
          <Text style={styles.statValue}>
            {stats ? Math.round(stats.total_focused_hrs) : 0}
          </Text>
          <Text style={styles.statLabel}>Focus Hours</Text>
        </View>

        {/* Notes Taken Card */}
        <View style={styles.card}>
          <Ionicons name="document-text-outline" size={32} color="#F5A623" />
          <Text style={styles.statValue}>
            {stats ? stats.total_notes : 0}
          </Text>
          <Text style={styles.statLabel}>Notes Taken</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    letterSpacing: 1,
    marginBottom: 12,
  },
  loadingContainer: {
    height: 140,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  card: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F2937',
    marginTop: 10,
  },
  statLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280',
    marginTop: 4,
  },
});

export default DashboardQuantifiedProgress;
