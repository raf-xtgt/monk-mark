import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  FlatList,
  TouchableOpacity,
  useWindowDimensions,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import DashboardLegacyArtCard from './_dashboard-legacy-art-card';
import { DashboardLegacyArtByHdr } from '../../_model/dto/_dashboard-dto';

const ITEMS_PER_PAGE = 3;

interface DashboardLegacyArtListingProps {
  arts: DashboardLegacyArtByHdr[] | null;
  isLoading: boolean;
}

const DashboardLegacyArtListing: React.FC<DashboardLegacyArtListingProps> = ({ arts, isLoading }) => {
  const { width } = useWindowDimensions();
  const [currentPage, setCurrentPage] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const items = (arts || []).filter(
    (art) => art.reward_lines && art.reward_lines.length > 0
  );
  const totalPages = Math.max(Math.ceil(items.length / ITEMS_PER_PAGE), 1);

  // Compute page width matching the parent's responsive padding
  const horizontalPadding = Math.min(Math.max(width * 0.04, 12), 32);
  const pageWidth = width - horizontalPadding * 2;

  /**
   * Split arts into pages of ITEMS_PER_PAGE.
   */
  const getPages = (): DashboardLegacyArtByHdr[][] => {
    const pages: DashboardLegacyArtByHdr[][] = [];
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
    const measuredWidth = event.nativeEvent.layoutMeasurement.width;
    const page = Math.round(offsetX / measuredWidth);
    setCurrentPage(page);
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text style={styles.sectionTitle}>LEGACY ART GALLERY</Text>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
        </View>
      </View>
    );
  }

  const renderPage = ({ item }: { item: DashboardLegacyArtByHdr[] }) => (
    <View style={[styles.page, { width: pageWidth }]}>
      {item.map((artHdr) => (
        <DashboardLegacyArtCard key={artHdr.reward_hdr_guid} artHdr={artHdr} />
      ))}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header with title and pagination */}
      <View style={styles.header}>
        <Text style={styles.sectionTitle}>LEGACY ART GALLERY</Text>
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

      {/* Horizontally scrollable art pages */}
      {items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="image-outline" size={36} color="#D1D5DB" />
          <Text style={styles.emptyText}>No legacy art yet</Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={pages}
          renderItem={renderPage}
          keyExtractor={(_, index) => `art-page-${index}`}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          onMomentumScrollEnd={handleScrollEnd}
          getItemLayout={(_, index) => ({
            length: pageWidth,
            offset: pageWidth * index,
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
    height: 140,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    height: 120,
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
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignItems: 'flex-start',
    gap: 12,
    paddingVertical: 8,
  },
});

export default DashboardLegacyArtListing;
