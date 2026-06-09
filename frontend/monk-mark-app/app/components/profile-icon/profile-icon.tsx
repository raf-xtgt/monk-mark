import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { useAppState } from '../../_state-controller/state-controller';

interface ProfileIconProps {
  onPress: () => void;
}

const ProfileIcon: React.FC<ProfileIconProps> = ({ onPress }) => {
  const { user } = useAppState();

  const getInitials = () => {
    if (!user?.userName) return 'U';
    return user.userName.substring(0, 2).toUpperCase();
  };

  return (
    <TouchableOpacity onPress={onPress} style={styles.container}>
      <View style={styles.circle}>
        <Text style={styles.initials}>{getInitials()}</Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 4,
  },
  circle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#bb86fc',
    justifyContent: 'center',
    alignItems: 'center',
  },
  initials: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default ProfileIcon;
