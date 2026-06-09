import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { DashboardLegacyArtByHdr, RewardLine } from '../../_model/dto/_dashboard-dto';
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
    .map((line: RewardLine) => line.image_url)
    .filter((url): url is string => !!url);

  // Collect tier levels corresponding to each image
  const tierLevels = lines
    .filter((line: RewardLine) => !!line.image_url)
    .map((line: RewardLine) => line.tier_level);

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
          {stackedLines.map((line: RewardLine, index: number) => (
            <Image
              key={line.guid}
              source={{ uri: line.image_url || undefined }}
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

        {/* Tier label */}
        {/* <Text style={styles.tierLabel} numberOfLines={1}>
          {tierLevel != null ? `Tier ${tierLevel}` : 'Legacy Art'}
        </Text> */}
      </TouchableOpacity>

      {/* Reward dialog with paginated images */}
      <MonkModeRewardDialogue
        visible={dialogVisible}
        imageUrl={imageUrls.length > 0 ? imageUrls[0] : null}
        images={imageUrls}
        tierLevels={tierLevels}
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
  tierLabel: {
    marginTop: 10,
    fontSize: 11,
    fontWeight: '500',
    color: '#6B7280',
    textAlign: 'center',
  },
});

export default DashboardLegacyArtCard;
