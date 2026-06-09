import React, { useEffect, useRef, useMemo } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { MilestoneEvaluation } from '../../_model/dto/reward-output-dto';

interface ProgressAuraProps {
  milestone: MilestoneEvaluation | null;
  children: React.ReactNode;
}

const RING_SIZE = 220;
const STROKE_WIDTH = 6;
const RADIUS = (RING_SIZE - STROKE_WIDTH) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// Segment allocation: 70% for focus hours, 30% for notes
const FOCUS_SEGMENT_RATIO = 0.7;
const NOTES_SEGMENT_RATIO = 0.3;
const FOCUS_ARC_LENGTH = CIRCUMFERENCE * FOCUS_SEGMENT_RATIO;
const NOTES_ARC_LENGTH = CIRCUMFERENCE * NOTES_SEGMENT_RATIO;

// Colors
const FOCUS_COLOR = '#4ecdc4';       // Teal
const NOTES_COLOR = '#f4c542';       // Gold
const TRACK_FOCUS = 'rgba(78, 205, 196, 0.15)';
const TRACK_NOTES = 'rgba(244, 197, 66, 0.15)';

// Rotation offsets (starting from top, -90deg)
// Focus arc starts at -90 (top) and spans 70% clockwise (252 degrees)
// Notes arc starts where focus ends: -90 + 252 = 162 degrees
const FOCUS_START_ROTATION = -90;
const NOTES_START_ROTATION = -90 + (360 * FOCUS_SEGMENT_RATIO); // 162

const ProgressAura: React.FC<ProgressAuraProps> = ({ milestone, children }) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;

  const focusProgress = useMemo(() => {
    if (!milestone) return 0;
    return Math.max(0, Math.min(100, milestone.hour_completion_percentage));
  }, [milestone?.hour_completion_percentage]);

  const noteProgress = useMemo(() => {
    if (!milestone) return 0;
    return Math.max(0, Math.min(100, milestone.note_completion_percentage));
  }, [milestone?.note_completion_percentage]);

  // Stroke dash offsets for each segment
  const focusDashoffset = useMemo(() => {
    return FOCUS_ARC_LENGTH - (focusProgress / 100) * FOCUS_ARC_LENGTH;
  }, [focusProgress]);

  const notesDashoffset = useMemo(() => {
    return NOTES_ARC_LENGTH - (noteProgress / 100) * NOTES_ARC_LENGTH;
  }, [noteProgress]);

  const bothFulfilled = (milestone?.is_hour_fulfilled && milestone?.is_note_fulfilled) ?? false;

  // Pulse animation when both thresholds are fulfilled
  useEffect(() => {
    if (bothFulfilled) {
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.06,
            duration: 1200,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1200,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      );
      pulse.start();
      return () => pulse.stop();
    } else {
      pulseAnim.setValue(1);
    }
  }, [bothFulfilled]);

  const tierLabel = useMemo(() => {
    if (!milestone) return '';
    const tierNames = ['I', 'II', 'III', 'IV', 'V'];
    const nextTierIndex = Math.min(milestone.next_tier - 1, tierNames.length - 1);
    return `Evolution ${tierNames[nextTierIndex]}`;
  }, [milestone?.next_tier]);

  return (
    <View style={styles.container}>
      {/* Progress Ring */}
      <Animated.View style={[styles.ringContainer, { transform: [{ scale: pulseAnim }] }]}>
        <Svg width={RING_SIZE} height={RING_SIZE} style={styles.svg}>
          {/* Focus background track (70%) */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={TRACK_FOCUS}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${FOCUS_ARC_LENGTH} ${CIRCUMFERENCE - FOCUS_ARC_LENGTH}`}
            strokeLinecap="round"
            rotation={FOCUS_START_ROTATION}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />
          {/* Notes background track (30%) */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={TRACK_NOTES}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${NOTES_ARC_LENGTH} ${CIRCUMFERENCE - NOTES_ARC_LENGTH}`}
            strokeLinecap="round"
            rotation={NOTES_START_ROTATION}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />
          {/* Focus active arc */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={FOCUS_COLOR}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${FOCUS_ARC_LENGTH} ${CIRCUMFERENCE - FOCUS_ARC_LENGTH}`}
            strokeDashoffset={bothFulfilled ? 0 : focusDashoffset}
            strokeLinecap="round"
            rotation={FOCUS_START_ROTATION}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />
          {/* Notes active arc */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={NOTES_COLOR}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${NOTES_ARC_LENGTH} ${CIRCUMFERENCE - NOTES_ARC_LENGTH}`}
            strokeDashoffset={bothFulfilled ? 0 : notesDashoffset}
            strokeLinecap="round"
            rotation={NOTES_START_ROTATION}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />
        </Svg>

        {/* Book cover (children) centered inside the ring */}
        <View style={styles.childContainer}>
          {children}
        </View>
      </Animated.View>

      {/* Tier label */}
      {/* {milestone && (
        <Text style={styles.tierLabel}>{tierLabel}</Text>
      )} */}

      {/* Segment legend */}
      {milestone && (
        <View style={styles.legendContainer}>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: FOCUS_COLOR }]} />
            <Text style={styles.legendText}>Focus</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: NOTES_COLOR }]} />
            <Text style={styles.legendText}>Notes</Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  ringContainer: {
    width: RING_SIZE,
    height: RING_SIZE,
    alignItems: 'center',
    justifyContent: 'center',
  },
  svg: {
    position: 'absolute',
  },
  childContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  tierLabel: {
    marginTop: 12,
    fontSize: 14,
    fontWeight: '600',
    color: '#4ecdc4',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  legendContainer: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendText: {
    fontSize: 11,
    color: '#ffffff',
    opacity: 0.7,
  },
});

export default ProgressAura;
