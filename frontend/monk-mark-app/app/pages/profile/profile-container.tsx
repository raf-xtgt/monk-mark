import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useAppState } from '../../_state-controller/state-controller';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ProfileContainer: React.FC = () => {
  const { user } = useAppState();

  const handleDeleteUser = async () => {
    Alert.alert(
      'Delete User Data',
      'Are you sure you want to delete your user data? This will log you out.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('UserStateDto.guid');
              await AsyncStorage.removeItem('UserStateDto.userName');
              await AsyncStorage.removeItem('UserStateDto.email');
              Alert.alert('Success', 'User data deleted. Please restart the app.');
            } catch (error) {
              console.error('Error deleting user data:', error);
              Alert.alert('Error', 'Failed to delete user data');
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.profileCircle}>
        <Text style={styles.initials}>
          {user?.userName ? user.userName.substring(0, 2).toUpperCase() : 'U'}
        </Text>
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.label}>Username</Text>
        <Text style={styles.value}>{user?.userName || 'Not set'}</Text>

        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user?.email || 'Not set'}</Text>
      </View>

      <TouchableOpacity style={styles.deleteButton} onPress={handleDeleteUser}>
        <Text style={styles.deleteButtonText}>Delete User Data</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    paddingTop: 40,
    backgroundColor: '#f5f5f5',
  },
  profileCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  initials: {
    color: '#ffffff',
    fontSize: 40,
    fontWeight: 'bold',
  },
  infoContainer: {
    width: '90%',
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 20,
  },
  label: {
    fontSize: 12,
    color: '#666666',
    marginTop: 15,
    marginBottom: 5,
    fontWeight: '600',
  },
  value: {
    fontSize: 18,
    color: '#000000',
    marginBottom: 10,
  },
  valueSmall: {
    fontSize: 14,
    color: '#000000',
    marginBottom: 10,
  },
  deleteButton: {
    marginTop: 30,
    backgroundColor: '#d32f2f',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
  },
  deleteButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileContainer;
