import React from 'react';
import { View, StyleSheet } from 'react-native';
import DashboardView from '@/app/components/_dashboard-components/_dashboard-view';

const HomeContainer: React.FC = () => {
  return (
    <View style={styles.container}>
      {/* <HomeDashboard /> */}
      <DashboardView />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});

export default HomeContainer;
