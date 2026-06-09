import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';

interface LibraryCardProps {
  bookName: string;
  coverImageUrl?: string;
  totalSessions: number;
  focusTime: string;
  onPress?: () => void;
}

const LibraryCard: React.FC<LibraryCardProps> = ({
  bookName,
  coverImageUrl,
  totalSessions,
  focusTime,
  onPress,
}) => {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.imageContainer}>
        {coverImageUrl ? (
          <Image source={{ uri: coverImageUrl }} style={styles.bookImage} resizeMode="cover" />
        ) : (
          <View style={styles.placeholderImage}>
            <Text style={styles.placeholderText}>📚</Text>
          </View>
        )}
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.bookName} numberOfLines={2} ellipsizeMode="tail">
          {bookName}
        </Text>

        <View style={styles.statsContainer}>
          <View style={styles.statRow}>
            <View style={styles.iconCircle}>
              <Text style={styles.statIcon}>⏱</Text>
            </View>
            <Text style={styles.statText}>{focusTime}</Text>
          </View>
          <View style={styles.statRow}>
            <View style={styles.iconCircle}>
              <Text style={styles.statIcon}>📖</Text>
            </View>
            <Text style={styles.statText}>{totalSessions} sessions</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  imageContainer: {
    width: '100%',
    flex: 1,
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 8,
  },
  bookImage: {
    width: '100%',
    height: '100%',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
    backgroundColor: '#e0e0e0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 48,
  },
  infoContainer: {
    minHeight: 70,
  },
  bookName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 6,
    height: 36,
  },
  statsContainer: {
    gap: 6,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  iconCircle: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statIcon: {
    fontSize: 12,
  },
  statText: {
    fontSize: 11,
    color: '#888',
    fontWeight: '400',
  },
});

export default LibraryCard;
