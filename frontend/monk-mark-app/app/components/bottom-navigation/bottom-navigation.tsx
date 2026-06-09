import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { routes } from '../../router';

interface BottomNavigationProps {
  currentRoute: number;
  onNavigate: (routeId: number) => void;
}

const BottomNavigation: React.FC<BottomNavigationProps> = ({ currentRoute, onNavigate }) => {
  const regularRoutes = routes.filter(r => r.id !== 4 && r.id !== 6); // Exclude MonkMode and NoteTaker
  const monkModeRoute = routes.find(r => r.id === 4); // MonkMode route

  return (
    <View style={styles.container}>
      <View style={styles.navBar}>
        {/* First two tabs */}
        {regularRoutes.slice(0, 2).map((route) => (
          <TouchableOpacity
            key={route.id}
            style={styles.tab}
            onPress={() => onNavigate(route.id)}
          >
            <Text style={[
              styles.icon,
              currentRoute === route.id && styles.activeIcon
            ]}>
              {route.id === 1 ? '🏠' : '📖'}
            </Text>
            <Text style={[
              styles.tabText,
              currentRoute === route.id && styles.activeTabText
            ]}>
              {route.name}
            </Text>
          </TouchableOpacity>
        ))}

        {/* Center circular button for MonkMode */}
        {/* <View style={styles.centerButtonContainer}>
          <TouchableOpacity
            style={styles.centerButton}
            onPress={() => monkModeRoute && onNavigate(monkModeRoute.id)}
          >
            <Text style={styles.centerButtonText}>+</Text>
          </TouchableOpacity>
        </View> */}

        {/* Last two tabs */}
        {regularRoutes.slice(2).map((route) => (
          <TouchableOpacity
            key={route.id}
            style={styles.tab}
            onPress={() => onNavigate(route.id)}
          >
            <Text style={[
              styles.icon,
              currentRoute === route.id && styles.activeIcon
            ]}>
              {route.id === 3 ? '📝' : '👤'}
            </Text>
            <Text style={[
              styles.tabText,
              currentRoute === route.id && styles.activeTabText
            ]}>
              {route.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 5,
    paddingBottom: 15,
    backgroundColor: '#f5f5f5',
  },
  navBar: {
    height: 70,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    backgroundColor: '#ffffff',
    borderRadius: 45,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 10,
  },
  tab: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
  },
  icon: {
    fontSize: 24,
    marginBottom: 4,
    opacity: 0.5,
  },
  activeIcon: {
    opacity: 1,
  },
  tabText: {
    fontSize: 11,
    color: '#9e9e9e',
  },
  activeTabText: {
    color: '#000000',
    fontWeight: '600',
  },
  centerButtonContainer: {
    width: 70,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: -30,
  },
  centerButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
  centerButtonText: {
    fontSize: 32,
    color: '#757575',
    fontWeight: '300',
  },
});

export default BottomNavigation;
