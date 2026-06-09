import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, useWindowDimensions } from 'react-native';
import DashboardQuantifiedProgress from './_dashboard-quantified-progress';
import RecentReading from '../_home-components/home-components-recent-reading';
import NotebookListing from '../_notebook-components/_notebook-listing';
import NotebookView from '../_notebook-components/_notebook-view';
import DashboardLegacyArtListing from './_dashboard-legacy-art-listing';
import { DashboardService } from '../../_services/_dashboard-service';
import { LibraryService } from '../../_services/library-service';
import { DashboardStats, DashboardNotebook, DashboardLegacyArtByHdr } from '../../_model/dto/_dashboard-dto';
import { useAppState } from '../../_state-controller/state-controller';

const DashboardView: React.FC = () => {
  const { width } = useWindowDimensions();
  const { user } = useAppState();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  const [notebooks, setNotebooks] = useState<DashboardNotebook[] | null>(null);
  const [notebooksLoading, setNotebooksLoading] = useState(true);

  const [legacyArts, setLegacyArts] = useState<DashboardLegacyArtByHdr[] | null>(null);
  const [legacyArtsLoading, setLegacyArtsLoading] = useState(true);

  const [books, setBooks] = useState<any[] | null>(null);
  const [booksLoading, setBooksLoading] = useState(true);

  const [selectedNotebook, setSelectedNotebook] = useState<DashboardNotebook | null>(null);

  useEffect(() => {
    if (!user?.guid) {
      setStatsLoading(false);
      setNotebooksLoading(false);
      setLegacyArtsLoading(false);
      setBooksLoading(false);
      return;
    }

    const fetchAll = async () => {
      // Fetch data sequentially to avoid overwhelming free-tier Supabase

      // Stats
      try {
        const statsData = await DashboardService.getUserStats(user.guid);
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
      setStatsLoading(false);

      // Notebooks
      try {
        const notebooksData = await DashboardService.getUserNotebooks(user.guid);
        setNotebooks(notebooksData);
      } catch (error) {
        console.error('Failed to load notebooks:', error);
      }
      setNotebooksLoading(false);

      // Legacy Arts
      try {
        const legacyArtsData = await DashboardService.getUserLegacyArtsByHdr(user.guid);
        setLegacyArts(legacyArtsData);
      } catch (error) {
        console.error('Failed to load legacy arts:', error);
      }
      setLegacyArtsLoading(false);

      // Books
      try {
        const booksData = await LibraryService.getLibraryBookRecordsByCriteria({ user_guid: user.guid });
        setBooks(booksData || []);
      } catch (error) {
        console.error('Failed to load books:', error);
      }
      setBooksLoading(false);
    };

    fetchAll();
  }, [user?.guid]);

  const horizontalPadding = Math.min(Math.max(width * 0.04, 12), 32);

  const handleNotebookPress = (notebook: DashboardNotebook) => {
    setSelectedNotebook(notebook);
  };

  const handleNotebookBack = () => {
    setSelectedNotebook(null);
  };

  // Show NotebookView when a notebook is selected
  if (selectedNotebook) {
    return (
      <NotebookView
        notebookGuid={selectedNotebook.notebook_hdr_guid}
        notebookName={selectedNotebook.notebook_name}
        libraryHdrGuid={selectedNotebook.library_hdr_guid}
        onBack={handleNotebookBack}
      />
    );
  }

  return (
    <ScrollView
      style={styles.scrollView}
      contentContainerStyle={[styles.contentContainer, { paddingHorizontal: horizontalPadding }]}
      showsVerticalScrollIndicator={false}
      nestedScrollEnabled
    >
        {/* Quantified progress section */}
        <View>
          <DashboardQuantifiedProgress stats={stats} isLoading={statsLoading} />
        </View>

        {/* My Notebooks section */}
        <View>
          <NotebookListing notebooks={notebooks} isLoading={notebooksLoading} onNotebookPress={handleNotebookPress} />
        </View>

        {/* Legacy Art Gallery */}
        <View>
          <DashboardLegacyArtListing arts={legacyArts} isLoading={legacyArtsLoading} />
        </View>

        {/* Recent Focus section */}
        <View>
          <RecentReading books={books} isLoading={booksLoading} />
        </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  contentContainer: {
    paddingVertical: 16,
    flexGrow: 1,
  },
});

export default DashboardView;
