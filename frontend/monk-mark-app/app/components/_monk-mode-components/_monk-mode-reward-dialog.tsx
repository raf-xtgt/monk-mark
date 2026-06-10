import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Modal, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface MonkModeRewardDialogueProps {
  visible: boolean;
  imageUrl: string | null;
  /** Optional array of image URLs for paginated gallery mode */
  images?: string[];
  /** Optional single tier level (used when only one image) */
  tierLevel?: number;
  /** Optional array of tier levels corresponding to each image */
  tierLevels?: (number | null)[];
  /** Optional GitLab issue URL */
  issueUrl?: string | null;
  /** Optional GitLab merge request URL */
  mrUrl?: string | null;
  onClose: () => void;
  onGalleryPress: () => void;
}

const MonkModeRewardDialogue: React.FC<MonkModeRewardDialogueProps> = ({
  visible,
  imageUrl,
  images,
  tierLevel,
  tierLevels,
  issueUrl,
  mrUrl,
  onClose,
  onGalleryPress,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Use images array if provided, otherwise fall back to single imageUrl
  // Sort by tier level ascending when tierLevels are provided
  const rawImageList = images && images.length > 0 ? images : imageUrl ? [imageUrl] : [];
  const rawTierLevels = tierLevels || [];

  // Build paired array and sort by tier level ascending
  const paired = rawImageList.map((url, i) => ({
    url,
    tier: rawTierLevels[i] ?? null,
  }));

  if (rawTierLevels.length > 0) {
    paired.sort((a, b) => (a.tier ?? 0) - (b.tier ?? 0));
  }

  const imageList = paired.map((p) => p.url);
  const sortedTierLevels = paired.map((p) => p.tier);

  const totalImages = imageList.length;
  const hasMultipleImages = totalImages > 1;

  const currentImageUrl = totalImages > 0 ? imageList[currentIndex] : null;

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const goToNext = () => {
    if (currentIndex < totalImages - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  // Reset index when dialog opens/closes
  const handleClose = () => {
    setCurrentIndex(0);
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={handleClose}
    >
      <View style={styles.overlay}>
        <View style={styles.dialogBox}>
          {/* Close button */}
          <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>

          {/* Title */}
          <Text style={styles.title}>Legacy Art Unlocked</Text>

          {/* Pagination controls (only if multiple images) */}
          {hasMultipleImages && (
            <View style={styles.paginationRow}>
              <TouchableOpacity
                onPress={goToPrevious}
                disabled={currentIndex === 0}
                style={styles.navButton}
              >
                <Ionicons
                  name="chevron-back"
                  size={20}
                  color={currentIndex === 0 ? '#D1D5DB' : '#333'}
                />
              </TouchableOpacity>
              <Text style={styles.paginationText}>
                {currentIndex + 1} of {totalImages}
              </Text>
              <TouchableOpacity
                onPress={goToNext}
                disabled={currentIndex === totalImages - 1}
                style={styles.navButton}
              >
                <Ionicons
                  name="chevron-forward"
                  size={20}
                  color={currentIndex === totalImages - 1 ? '#D1D5DB' : '#333'}
                />
              </TouchableOpacity>
            </View>
          )}

          {/* Art image */}
          {currentImageUrl ? (
            <Image
              source={{ uri: currentImageUrl }}
              style={styles.artImage}
              resizeMode="contain"
            />
          ) : (
            <View style={styles.placeholderImage}>
              <Ionicons name="image-outline" size={48} color="#ccc" />
            </View>
          )}

          {/* Tier level */}
          {(() => {
            const currentTier = sortedTierLevels[currentIndex] != null
              ? sortedTierLevels[currentIndex]
              : tierLevel;
            return currentTier != null ? (
              <Text style={styles.tierText}>Tier {currentTier}</Text>
            ) : null;
          })()}

          {/* GitLab links */}
          {(issueUrl || mrUrl) && (
            <View style={styles.gitlabLinksContainer}>
              {issueUrl && (
                <TouchableOpacity
                  style={styles.gitlabLink}
                  onPress={() => Linking.openURL(issueUrl)}
                >
                  <Ionicons name="git-branch-outline" size={16} color="#6366F1" />
                  <Text style={styles.gitlabLinkText}>View Issue</Text>
                </TouchableOpacity>
              )}
              {mrUrl && (
                <TouchableOpacity
                  style={styles.gitlabLink}
                  onPress={() => Linking.openURL(mrUrl)}
                >
                  <Ionicons name="git-merge-outline" size={16} color="#6366F1" />
                  <Text style={styles.gitlabLinkText}>View Merge Request</Text>
                </TouchableOpacity>
              )}
            </View>
          )}

          {/* Gallery button */}
          <TouchableOpacity style={styles.galleryButton} onPress={onGalleryPress}>
            <Text style={styles.galleryButtonText}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  dialogBox: {
    width: '100%',
    maxWidth: 320,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    position: 'relative',
  },
  closeButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
    marginTop: 8,
  },
  paginationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  navButton: {
    padding: 4,
  },
  paginationText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
  },
  artImage: {
    width: 220,
    height: 220,
    borderRadius: 12,
    marginBottom: 12,
  },
  placeholderImage: {
    width: 220,
    height: 220,
    borderRadius: 12,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  tierText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 16,
  },
  galleryButton: {
    backgroundColor: '#4ecdc4',
    paddingHorizontal: 28,
    paddingVertical: 12,
    borderRadius: 10,
  },
  galleryButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#ffffff',
  },
  gitlabLinksContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  gitlabLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#EEF2FF',
    borderRadius: 8,
  },
  gitlabLinkText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6366F1',
  },
});

export default MonkModeRewardDialogue;
