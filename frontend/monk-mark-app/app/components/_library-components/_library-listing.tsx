import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, ActivityIndicator, Dimensions, TouchableOpacity } from 'react-native';
import { LibraryService } from '../../_services/library-service';
import { useAppState } from '../../_state-controller/state-controller';
import LibraryCard from './_library_card';

interface LibraryBook {
  guid: string;
  book_name: string;
  storage_path?: string;
  session_count?: number;
  focus_time?: string;
}

const CARD_MIN_WIDTH = 150;
const CARD_MAX_WIDTH = 200;
const CARD_HEIGHT = 280;
const CARD_GAP = 16;

const LibraryListing: React.FC = () => {
  const { user, setCurrentRoute, setFocusSession } = useAppState();
  const [books, setBooks] = useState<LibraryBook[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [numColumns, setNumColumns] = useState(2);
  const [cardWidth, setCardWidth] = useState(CARD_MIN_WIDTH);

  const calculateLayout = () => {
    const screenWidth = Dimensions.get('window').width;
    const availableWidth = screenWidth - (CARD_GAP * 2);

    let columns = Math.floor(availableWidth / (CARD_MIN_WIDTH + CARD_GAP));
    columns = Math.max(1, columns);

    const totalGapWidth = CARD_GAP * (columns - 1);
    const calculatedCardWidth = (availableWidth - totalGapWidth) / columns;
    const finalCardWidth = Math.min(calculatedCardWidth, CARD_MAX_WIDTH);

    setNumColumns(columns);
    setCardWidth(finalCardWidth);
  };

  useEffect(() => {
    calculateLayout();

    const subscription = Dimensions.addEventListener('change', calculateLayout);
    return () => subscription?.remove();
  }, []);

  const fetchBooks = async (bookName?: string) => {
    if (!user?.guid) return;

    try {
      setLoading(true);
      setError(null);

      const payload: any = {
        user_guid: user.guid,
      };

      if (bookName && bookName.trim()) {
        payload.book_name = bookName.trim();
      }

      const result = await LibraryService.getLibraryBookRecordsByCriteria(payload);

      const booksData = Array.isArray(result) ? result : [];
      setBooks(booksData);
    } catch (err) {
      console.error('Error fetching books:', err);
      setError('Failed to load library books');
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, [user?.guid]);

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      fetchBooks();
    } else {
      fetchBooksWithSearch(searchQuery);
    }
  };

  const fetchBooksWithSearch = async (bookName: string) => {
    if (!user?.guid) return;

    try {
      setLoading(true);
      setError(null);

      const payload = {
        user_guid: user.guid,
        book_name: bookName.trim(),
      };

      const result = await LibraryService.searchAndGetByCriteria(payload);

      const booksData = Array.isArray(result) ? result : [];
      setBooks(booksData);
    } catch (err) {
      console.error('Error searching books:', err);
      setError('Failed to search library books');
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookPress = (book: LibraryBook) => {
    if (!user?.guid) return;

    // Map book data to FocusSessionDto
    const focusSessionData = {
      userGuid: user.guid,
      focusSessionGuid: '',
      libraryHdrGuid: book.guid,
      bookName: book.book_name,
      coverImageUrl: book.storage_path || '',
    };

    // Store in state
    setFocusSession(focusSessionData);

    // Navigate to Monk Mode
    setCurrentRoute(4);
  };

  const renderItem = ({ item }: { item: LibraryBook }) => (
    <View style={[styles.cardWrapper, { width: cardWidth, height: CARD_HEIGHT }]}>
      <LibraryCard
        bookName={item.book_name}
        coverImageUrl={item.storage_path}
        totalSessions={item.session_count || 0}
        focusTime={item.focus_time || '0h 0min'}
        onPress={() => handleBookPress(item)}
      />
    </View>
  );

  const renderEmptyComponent = () => {
    if (loading) {
      return (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#6200ee" />
          <Text style={styles.loadingText}>Loading your library...</Text>
        </View>
      );
    }

    if (error) {
      return (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      );
    }

    return (
      <View style={styles.centerContainer}>
        <Text style={styles.emptyText}>
          {searchQuery ? 'No books found matching your search' : 'Your library is empty'}
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Search view */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search library"
          placeholderTextColor="#999"
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TouchableOpacity onPress={handleSearch} style={styles.searchIconButton}>
          <Text style={styles.searchIcon}>🔍</Text>
        </TouchableOpacity>
      </View>

      {/* Library book listing view */}
      <FlatList
        data={books}
        renderItem={renderItem}
        keyExtractor={(item) => item.guid}
        numColumns={numColumns}
        key={numColumns}
        columnWrapperStyle={numColumns > 1 ? styles.row : undefined}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmptyComponent}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchContainer: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#ffffff',
  },
  searchIcon: {
    fontSize: 20,
  },
  searchIconButton: {
    position: 'absolute',
    right: 20,
    padding: 8,
  },
  listContent: {
    padding: 16,
    flexGrow: 1,
  },
  row: {
    justifyContent: 'flex-start',
    gap: CARD_GAP,
  },
  cardWrapper: {
    marginBottom: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#d32f2f',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
});

export default LibraryListing;
