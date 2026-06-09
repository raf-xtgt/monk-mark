import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import ProfileIcon from '../profile-icon/profile-icon';
import { useAppState } from '../../_state-controller/state-controller';

const TopBar: React.FC = () => {
  const { setCurrentRoute } = useAppState();

  const handleProfilePress = () => {
    setCurrentRoute(5); // Profile route ID from router.tsx
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Monk Mark</Text>
      <View style={styles.rightSection}>
        <ProfileIcon onPress={handleProfilePress} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 60,
    backgroundColor: '#6200ee',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  title: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  rightSection: {
    position: 'absolute',
    right: 10,
  },
});

export default TopBar;
