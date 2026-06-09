import React from 'react';
import { View, StyleSheet } from 'react-native';
import LibraryListing from '@/app/components/_library-components/_library-listing';

const LibraryContainer: React.FC = () => {
  return (
    <View style={styles.container}>
      <LibraryListing />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});

export default LibraryContainer;
