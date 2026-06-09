import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  FlatList,
  useWindowDimensions,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DashboardNotebook } from '../../_model/dto/_dashboard-dto';

const ITEMS_PER_PAGE = 3;

interface NotebookListingProps {
  notebooks: DashboardNotebook[] | null;
  isLoading: boolean;
  onNotebookPress?: (notebook: DashboardNotebook) => void;
}

const NotebookListing: React.FC<NotebookListingProps> = ({ notebooks, isLoading, onNotebookPress }) => {
  const { width } = useWindowDimensions();
  const [currentPage, setCurrentPage] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const items = notebooks || [];
  const totalPages = Math.max(Math.ceil(items.length / ITEMS_PER_PAGE), 1);

  /**
   * Format the last_updated timestamp into a human-readable relative string.
   */
  const formatLastUpdated = (dateStr: string | null): string => {
    if (!dateStr) return 'No activity yet';

    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Last updated just now';
    if (diffMins < 60) return `Last updated ${diffMins}m ago`;
    if (diffHours < 24) return `Last updated ${diffHours}h ago`;
    if (diffDays === 1) return 'Last updated yesterday';
    if (diffDays < 7) return `Last updated ${diffDays}d ago`;
    return `Last updated ${date.toLocaleDateString()}`;
  };

  /**
   * Split notebooks into pages of ITEMS_PER_PAGE.
   */
  const getPages = (): DashboardNotebook[][] => {
    const pages: DashboardNotebook[][] = [];
    for (let i = 0; i < items.length; i += ITEMS_PER_PAGE) {
      pages.push(items.slice(i, i + ITEMS_PER_PAGE));
    }
    return pages.length > 0 ? pages : [[]];
  };

  const pages = getPages();

  const goToPage = (page: number) => {
    if (page < 0 || page >= totalPages) return;
    setCurrentPage(page);
    flatListRef.current?.scrollToIndex({ index: page, animated: true });
  };

  const handleScrollEnd = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const offsetX = event.nativeEvent.contentOffset.x;
    const pageWidth = event.nativeEvent.layoutMeasurement.width;
    const page = Math.round(offsetX / pageWidth);
    setCurrentPage(page);
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text style={styles.sectionTitle}>MY NOTEBOOKS</Text>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
        </View>
      </View>
    );
  }

  const renderPage = ({ item }: { item: DashboardNotebook[] }) => (
    <View style={[styles.page, { width: width - Math.min(Math.max(width * 0.04, 12), 32) * 2 }]}>
      {item.map((notebook) => (
        <TouchableOpacity
          key={notebook.notebook_hdr_guid}
          style={styles.notebookRow}
          activeOpacity={0.7}
          onPress={() => onNotebookPress?.(notebook)}
        >
          <View style={styles.iconContainer}>
            <Ionicons name="leaf" size={20} color="#FFFFFF" />
          </View>
          <View style={styles.notebookInfo}>
            <Text style={styles.notebookName} numberOfLines={1}>
              {notebook.notebook_name}
            </Text>
            <Text style={styles.notebookMeta}>
              {formatLastUpdated(notebook.last_updated)}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header with title and pagination controls */}
      <View style={styles.header}>
        <Text style={styles.sectionTitle}>MY NOTEBOOKS</Text>
        <View style={styles.paginationControls}>
          <TouchableOpacity
            onPress={() => goToPage(currentPage - 1)}
            disabled={currentPage === 0}
            style={styles.pageButton}
          >
            <Ionicons
              name="chevron-back"
              size={18}
              color={currentPage === 0 ? '#D1D5DB' : '#6B7280'}
            />
          </TouchableOpacity>
          <Text style={styles.pageIndicator}>
            Page {currentPage + 1} of {totalPages}
          </Text>
          <TouchableOpacity
            onPress={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages - 1}
            style={styles.pageButton}
          >
            <Ionicons
              name="chevron-forward"
              size={18}
              color={currentPage === totalPages - 1 ? '#D1D5DB' : '#6B7280'}
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* Swipeable notebook pages */}
      {items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="book-outline" size={36} color="#D1D5DB" />
          <Text style={styles.emptyText}>No notebooks yet</Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={pages}
          renderItem={renderPage}
          keyExtractor={(_, index) => `page-${index}`}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          onMomentumScrollEnd={handleScrollEnd}
          getItemLayout={(_, index) => ({
            length: width - Math.min(Math.max(width * 0.04, 12), 32) * 2,
            offset: (width - Math.min(Math.max(width * 0.04, 12), 32) * 2) * index,
            index,
          })}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    letterSpacing: 1,
  },
  paginationControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  pageButton: {
    padding: 4,
  },
  pageIndicator: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
  },
  loadingContainer: {
    height: 180,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    height: 140,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    gap: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  page: {
    gap: 10,
  },
  notebookRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1F2937',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  notebookInfo: {
    flex: 1,
  },
  notebookName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  notebookMeta: {
    fontSize: 13,
    color: '#6B7280',
  },
});

export default NotebookListing;
