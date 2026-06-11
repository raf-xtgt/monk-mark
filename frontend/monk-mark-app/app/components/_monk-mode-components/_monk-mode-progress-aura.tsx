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

// Colors
const FOCUS_COLOR = '#4ecdc4';       // Teal
const NOTES_COLOR = '#f4c542';       // Gold
const TRACK_COLOR = 'rgba(255, 255, 255, 0.1)';

// Both arcs start from the top (-90 degrees) and fill clockwise.
// Focus uses the full circumference — its dasharray limits the visible portion.
// Notes uses the full circumference similarly.
const START_ROTATION = -90;

const ProgressAura: React.FC<ProgressAuraProps> = ({ milestone, children }) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Track peak progress within a session to prevent visual regression
  const peakFocusRef = useRef(0);
  const peakNotesRef = useRef(0);

  const focusProgress = useMemo(() => {
    if (!milestone) return 0;
    const raw = Math.max(0, Math.min(100, milestone.hour_completion_percentage));
    if (raw >= peakFocusRef.current) {
      peakFocusRef.current = raw;
    }
    return peakFocusRef.current;
  }, [milestone?.hour_completion_percentage, milestone?.current_tier]);

  const noteProgress = useMemo(() => {
    if (!milestone) return 0;
    const raw = Math.max(0, Math.min(100, milestone.note_completion_percentage));
    if (raw >= peakNotesRef.current) {
      peakNotesRef.current = raw;
    }
    return peakNotesRef.current;
  }, [milestone?.note_completion_percentage, milestone?.current_tier]);

  const bothFulfilled = (milestone?.is_hour_fulfilled && milestone?.is_note_fulfilled) ?? false;

  // Calculate the filled length for each arc.
  // Focus arc occupies 70% of the circumference, Notes arc occupies 30%.
  const focusArcLength = CIRCUMFERENCE * 0.7;
  const notesArcLength = CIRCUMFERENCE * 0.3;

  // The filled portion grows from 0 to the full arc length.
  // strokeDashoffset = arcLength - filledLength  (when positive, hides the tail)
  const focusFilled = bothFulfilled ? focusArcLength : (focusProgress / 100) * focusArcLength;
  const notesFilled = bothFulfilled ? notesArcLength : (noteProgress / 100) * notesArcLength;

  // strokeDasharray: [arcLength, gap] — where gap hides the rest of the ring
  // strokeDashoffset: shifts the dash pattern backwards to reveal from the start
  const focusDashoffset = focusArcLength - focusFilled;
  const notesDashoffset = notesArcLength - notesFilled;

  // Notes arc starts where focus arc ends: -90 + 252 = 162 degrees
  const notesRotation = START_ROTATION + 360 * 0.7;

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

  return (
    <View style={styles.container}>
      {/* Progress Ring */}
      <Animated.View style={[styles.ringContainer, { transform: [{ scale: pulseAnim }] }]}>
        <Svg width={RING_SIZE} height={RING_SIZE} style={styles.svg}>
          {/* Full background track */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={TRACK_COLOR}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
          />

          {/* Focus active arc — starts at top, spans 70% of ring */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={FOCUS_COLOR}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${focusFilled} ${CIRCUMFERENCE - focusFilled}`}
            strokeLinecap="round"
            rotation={START_ROTATION}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />

          {/* Notes active arc — starts where focus ends, spans 30% of ring */}
          <Circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RADIUS}
            stroke={NOTES_COLOR}
            strokeWidth={STROKE_WIDTH}
            fill="transparent"
            strokeDasharray={`${notesFilled} ${CIRCUMFERENCE - notesFilled}`}
            strokeLinecap="round"
            rotation={notesRotation}
            origin={`${RING_SIZE / 2}, ${RING_SIZE / 2}`}
          />
        </Svg>

        {/* Book cover (children) centered inside the ring */}
        <View style={styles.childContainer}>
          {children}
        </View>
      </Animated.View>

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
