import MonkModeBookSearch from '@/app/components/_monk-mode-components/_monk-mode-book-search';
import MonkModeView from '@/app/components/_monk-mode-components/_monk-mode-view';
import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { useAppState } from '@/app/_state-controller/state-controller';

interface BookResult {
  guid: string;
  book_name: string;
  author_name: string;
  description: string;
  cover_image_url: string;
}

const MonkModeContainer: React.FC = () => {
  const [selectedBook, setSelectedBook] = useState<BookResult | null>(null);
  const { focusSession } = useAppState();

  useEffect(() => {
    // If there's a focus session in state, use it to populate selectedBook
    if (focusSession && focusSession.libraryHdrGuid) {
      setSelectedBook({
        guid: focusSession.libraryHdrGuid,
        book_name: focusSession.bookName,
        author_name: '', // Not available from focus session
        description: '', // Not available from focus session
        cover_image_url: focusSession.coverImageUrl,
      });
    }
  }, [focusSession]);

  const handleBookSelect = (book: BookResult) => {
    setSelectedBook(book);
  };

  return (
    <View style={styles.container}>
      {!selectedBook ? (
        <MonkModeBookSearch onBookSelect={handleBookSelect} />
      ) : (
        <MonkModeView selectedBook={selectedBook} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});

export default MonkModeContainer;
