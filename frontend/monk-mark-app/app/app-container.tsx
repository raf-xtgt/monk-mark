import React, { useEffect } from 'react';
import { Platform, View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as NavigationBar from 'expo-navigation-bar';
import { useAppState } from './_state-controller/state-controller';
import TopBar from './components/top-bar/top-bar';
import BottomNavigation from './components/bottom-navigation/bottom-navigation';
import Router from './router';
import { SessionService } from './_services/session-service';

const AppContainer: React.FC = () => {
  const { showTopBar, showBottomNavigation, currentRoute, setCurrentRoute, setUser } = useAppState();

  useEffect(() => {
    if (Platform.OS === 'android') {
      NavigationBar.setVisibilityAsync('hidden');
      NavigationBar.setBehaviorAsync('overlay-swipe');
    }
  }, []);

  useEffect(() => {
    const initializeUser = async () => {
      try {
        const userState = await SessionService.getOrCreateUser({
          email: 'test-user@gmail.com',
        });
        setUser(userState);
      } catch (error) {
        console.error('Failed to initialize user:', error);
      }
    };

    initializeUser();
  }, [setUser]);

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      {showTopBar && <TopBar />}

      <View style={styles.content}>
        <Router currentRoute={currentRoute} />
      </View>

      {showBottomNavigation && (
        <BottomNavigation
          currentRoute={currentRoute}
          onNavigate={setCurrentRoute}
          backgroundColor={currentRoute === 4 ? '#4a4a5e' : undefined}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  content: {
    flex: 1,
  },
});

export default AppContainer;
