import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useAppState } from '../../_state-controller/state-controller';
import { Ionicons } from '@expo/vector-icons';

interface BookRecord {
  guid: string;
  book_name: string;
  book_desc: string;
  storage_path: string;
  last_read: string;
}

interface RecentReadingProps {
  books: BookRecord[] | null;
  isLoading: boolean;
}

const RecentReading: React.FC<RecentReadingProps> = ({ books, isLoading }) => {
  const { user, setCurrentRoute, setFocusSession } = useAppState();

  const handleViewAll = () => {
    setCurrentRoute(2); // Navigate to Library page
  };

  const handleBookPress = (book: BookRecord) => {
    if (!user?.guid) return;

    // Map book data to FocusSessionDto
    const focusSessionData = {
      userGuid: user.guid,
      focusSessionGuid: '',
      libraryHdrGuid: book.guid,
      bookName: book.book_name,
      coverImageUrl: book.storage_path,
    };

    // Store in state
    setFocusSession(focusSessionData);

    // Navigate to Monk Mode
    setCurrentRoute(4);
  };

  const items = books || [];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>CONTINUE READING</Text>
        {/* View All button */}
        <TouchableOpacity style={styles.viewAllButton} onPress={handleViewAll}>
          <Ionicons name="book" size={20} color="#000" />
          <Text style={styles.viewAllText}>View All</Text>
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
        </View>
      ) : items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No reading list yet</Text>
        </View>
      ) : (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {items.map((book) => (
            <TouchableOpacity key={book.guid} style={styles.bookCard} onPress={() => handleBookPress(book)}>
              {book.storage_path ? (
                <Image
                  source={{ uri: book.storage_path }}
                  style={styles.bookCover}
                  resizeMode="cover"
                  onError={(error) => console.log('Image load error:', error.nativeEvent.error)}
                />
              ) : (
                <View style={[styles.bookCover, styles.placeholderCover]}>
                  <Ionicons name="book" size={48} color="#ccc" />
                </View>
              )}
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    letterSpacing: 1,
  },
  viewAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  viewAllText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  scrollContent: {
    paddingRight: 20,
  },
  bookCard: {
    marginRight: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  bookCover: {
    width: 160,
    height: 240,
    borderRadius: 8,
  },
  placeholderCover: {
    backgroundColor: '#e0e0e0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    height: 240,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
  },
  emptyText: {
    fontSize: 16,
    color: '#9e9e9e',
    fontStyle: 'italic',
  },
});

export default RecentReading;
