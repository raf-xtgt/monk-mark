import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';

const { height } = Dimensions.get('window');

const NotebookBackground: React.FC = () => {
  // Calculate number of lines based on screen height
  const lineHeight = 40;
  const numberOfLines = Math.ceil(height / lineHeight);

  return (
    <View style={styles.container}>
      {/* Vertical red margin line */}
      <View style={styles.marginLine} />

      {/* Horizontal lines */}
      {Array.from({ length: numberOfLines }).map((_, index) => (
        <View key={index} style={styles.line} />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#fffef7', // Slightly off-white paper color
  },
  marginLine: {
    position: 'absolute',
    left: 40,
    top: 0,
    bottom: 0,
    width: 2,
    backgroundColor: '#ff6b6b',
    opacity: 0.6,
  },
  line: {
    height: 40,
    borderBottomWidth: 1,
    borderBottomColor: '#d4e4f7',
    opacity: 0.5,
  },
});

export default NotebookBackground;
