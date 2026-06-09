import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, FlatList, Text, Image, ActivityIndicator } from 'react-native';
import { LibraryService } from '../../_services/library-service';
import { useAppState } from '../../_state-controller/state-controller';

interface BookResult {
  guid: string;
  book_name: string;
  author_name: string;
  description: string;
  cover_image_url: string;
}

interface MonkModeBookSearchProps {
  onBookSelect: (book: BookResult) => void;
}

const MonkModeBookSearch: React.FC<MonkModeBookSearchProps> = ({ onBookSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<BookResult[]>([]);
  const [loading, setLoading] = useState(false);
  const { user, setFocusSession } = useAppState();

  const handleSearch = async () => {
    if (!searchQuery.trim() || !user?.guid) return;

    setLoading(true);
    try {
      const result = await LibraryService.bookSearch({
        book_name: searchQuery,
        user_guid: user.guid,
      });

      setSearchResults([result]);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookSelect = (book: BookResult) => {
    if (!user?.guid) return;

    // Map book data to FocusSessionDto
    const focusSessionData = {
      userGuid: user.guid,
      focusSessionGuid: '', // Will be set after creating the session
      libraryHdrGuid: book.guid,
      bookName: book.book_name,
      coverImageUrl: book.cover_image_url,
    };

    // Store in state
    setFocusSession(focusSessionData);
    
    // Call parent callback
    onBookSelect(book);
  };

  const truncateDescription = (description: string) => {
    const words = description.split(' ');
    return words.slice(0, 7).join(' ') + (words.length > 7 ? '...' : '');
  };

  const renderBookItem = ({ item }: { item: BookResult }) => (
    <TouchableOpacity style={styles.bookItem} onPress={() => handleBookSelect(item)}>
      <Image source={{ uri: item.cover_image_url }} style={styles.bookCover} />
      <View style={styles.bookInfo}>
        <Text style={styles.bookTitle}>{item.book_name}</Text>
        <Text style={styles.bookAuthor}>{item.author_name}</Text>
        {item.description && (
          <Text style={styles.bookDescription}>{truncateDescription(item.description)}</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchBar}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search for a book..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchIcon}>🔍</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#6200ee" style={styles.loader} />}

      <FlatList
        data={searchResults}
        renderItem={renderBookItem}
        keyExtractor={(item) => item.guid}
        contentContainerStyle={styles.resultsList}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 16,
  },
  searchInput: {
    flex: 1,
    height: 48,
    fontSize: 16,
  },
  searchButton: {
    padding: 8,
  },
  searchIcon: {
    fontSize: 20,
  },
  loader: {
    marginTop: 20,
  },
  resultsList: {
    paddingBottom: 16,
  },
  bookItem: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  bookCover: {
    width: 80,
    height: 120,
    borderRadius: 4,
    backgroundColor: '#e0e0e0',
  },
  bookInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  bookTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  bookAuthor: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  bookDescription: {
    fontSize: 12,
    color: '#999',
  },
});

export default MonkModeBookSearch;
