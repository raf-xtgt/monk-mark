import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { DashboardLegacyArtByHdr, RewardLineWithSyncLog } from '../../_model/dto/_dashboard-dto';
import { Ionicons } from '@expo/vector-icons';
import MonkModeRewardDialogue from '../_monk-mode-components/_monk-mode-reward-dialog';

interface DashboardLegacyArtCardProps {
  artHdr: DashboardLegacyArtByHdr;
}

const MAX_STACKED_IMAGES = 3;

const DashboardLegacyArtCard: React.FC<DashboardLegacyArtCardProps> = ({ artHdr }) => {
  const [dialogVisible, setDialogVisible] = useState(false);

  const lines = artHdr.reward_lines || [];
  // Show at most 3 stacked images
  const stackedLines = lines.slice(0, MAX_STACKED_IMAGES);

  // Collect all image URLs for the dialog
  const imageUrls = lines
    .map((entry: RewardLineWithSyncLog) => entry.reward_line.image_url)
    .filter((url): url is string => !!url);

  // Collect tier levels corresponding to each image
  const tierLevels = lines
    .filter((entry: RewardLineWithSyncLog) => !!entry.reward_line.image_url)
    .map((entry: RewardLineWithSyncLog) => entry.reward_line.tier_level);

  // Get the latest sync log (from the most recent reward line that has one)
  const latestSyncLog = [...lines]
    .reverse()
    .find((entry: RewardLineWithSyncLog) => entry.gitlab_sync_log != null)
    ?.gitlab_sync_log ?? null;

  const issueUrl = latestSyncLog?.issue_url ?? null;
  const mrUrl = latestSyncLog?.merge_request_url ?? null;
  const fileUrl = latestSyncLog?.file_url ?? null;

  const tierLevel = artHdr.reward_hdr_tier_level;

  const handlePress = () => {
    setDialogVisible(true);
  };

  const handleCloseDialog = () => {
    setDialogVisible(false);
  };

  return (
    <>
      <TouchableOpacity style={styles.card} onPress={handlePress} activeOpacity={0.8}>
        {/* Stacked images */}
        <View style={styles.stackContainer}>
          {stackedLines.map((entry: RewardLineWithSyncLog, index: number) => (
            <Image
              key={entry.reward_line.guid}
              source={{ uri: entry.reward_line.image_url || undefined }}
              style={[
                styles.stackedImage,
                {
                  top: index * 4,
                  left: index * 4,
                  zIndex: MAX_STACKED_IMAGES - index,
                },
              ]}
              resizeMode="cover"
            />
          ))}
          {stackedLines.length === 0 && (
            <View style={[styles.stackedImage, styles.placeholderImage]} />
          )}
        </View>

        {/* Sync indicator dot */}
        {latestSyncLog && (
          <View style={styles.syncIndicator}>
            <Ionicons name="git-merge-outline" size={10} color="#6366F1" />
          </View>
        )}
      </TouchableOpacity>

      {/* Reward dialog with paginated images and GitLab workflow steps */}
      <MonkModeRewardDialogue
        visible={dialogVisible}
        imageUrl={imageUrls.length > 0 ? imageUrls[0] : null}
        images={imageUrls}
        tierLevels={tierLevels}
        issueUrl={issueUrl}
        mrUrl={mrUrl}
        fileUrl={fileUrl}
        onClose={handleCloseDialog}
        onGalleryPress={handleCloseDialog}
      />
    </>
  );
};

const styles = StyleSheet.create({
  card: {
    width: 110,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    position: 'relative',
  },
  stackContainer: {
    width: 98,
    height: 98,
    position: 'relative',
  },
  stackedImage: {
    position: 'absolute',
    width: 86,
    height: 86,
    borderRadius: 10,
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  placeholderImage: {
    backgroundColor: '#E5E7EB',
  },
  syncIndicator: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#C7D2FE',
  },
});

export default DashboardLegacyArtCard;
