import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import NotebookListing from '@/app/components/_notebook-components/_notebook-listing';
import NotebookView from '@/app/components/_notebook-components/_notebook-view';
import { DashboardService } from '@/app/_services/_dashboard-service';
import { DashboardNotebook } from '@/app/_model/dto/_dashboard-dto';
import { useAppState } from '@/app/_state-controller/state-controller';

const NotebookContainer: React.FC = () => {
  const { user } = useAppState();
  const [notebooks, setNotebooks] = useState<DashboardNotebook[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNotebook, setSelectedNotebook] = useState<DashboardNotebook | null>(null);

  useEffect(() => {
    const fetchNotebooks = async () => {
      if (!user?.guid) {
        setIsLoading(false);
        return;
      }

      try {
        const result = await DashboardService.getUserNotebooks(user.guid);
        setNotebooks(result);
      } catch (error) {
        console.error('Failed to load notebooks:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNotebooks();
  }, [user?.guid]);

  const handleNotebookPress = (notebook: DashboardNotebook) => {
    setSelectedNotebook(notebook);
  };

  const handleBack = () => {
    setSelectedNotebook(null);
  };

  // Show NotebookView when a notebook is selected
  if (selectedNotebook) {
    return (
      <NotebookView
        notebookGuid={selectedNotebook.notebook_hdr_guid}
        notebookName={selectedNotebook.notebook_name}
        libraryHdrGuid={selectedNotebook.library_hdr_guid}
        onBack={handleBack}
      />
    );
  }

  return (
    <View style={styles.container}>
      <NotebookListing
        notebooks={notebooks}
        isLoading={isLoading}
        onNotebookPress={handleNotebookPress}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
    backgroundColor: '#f5f5f5',
  },
});

export default NotebookContainer;
