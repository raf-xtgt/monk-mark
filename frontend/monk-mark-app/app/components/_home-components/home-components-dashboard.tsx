import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import RecentReading from './home-components-recent-reading';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface CircularProgressProps {
  percentage: number;
  color: string;
  label: string;
}

const CircularProgress: React.FC<CircularProgressProps> = ({ percentage, color, label }) => {
  const animatedValue = useRef(new Animated.Value(0)).current;
  const size = 90;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: percentage,
      duration: 1500,
      useNativeDriver: true,
    }).start();
  }, [percentage]);

  const strokeDashoffset = animatedValue.interpolate({
    inputRange: [0, 100],
    outputRange: [circumference, 0],
  });

  return (
    <View style={styles.progressContainer}>
      <View style={styles.circleWrapper}>
        <Svg width={size} height={size}>
          {/* Background circle */}
          <Circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#f0f0f0"
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <AnimatedCircle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            rotation="-90"
            origin={`${size / 2}, ${size / 2}`}
          />
        </Svg>
        <View style={styles.percentageContainer}>
          <Text style={styles.percentageText}>{percentage}%</Text>
        </View>
      </View>
      <View style={styles.labelContainer}>
        <Text style={styles.labelText}>{label}</Text>
      </View>
    </View>
  );
};

const HomeDashboard: React.FC = () => {
  const depthScore = 9;

  const getDepthScoreColor = (score: number) => {
    if (score >= 7) return '#4caf50'; // Green
    if (score >= 4) return '#ffeb3b'; // Yellow
    return '#f44336'; // Red
  };

  const depthScoreColor = getDepthScoreColor(depthScore);

  return (
    <View style={styles.container}>
      {/* Date Header */}
      <View style={styles.header}>
        <Text style={styles.dateText}>Today, 25th January</Text>
      </View>

      {/* Depth Score Card */}
      <View style={styles.depthScoreCard}>
        <View style={[styles.iconCircle, { backgroundColor: depthScoreColor }]}>
          <Text style={styles.iconText}>🧠</Text>
        </View>
        <View style={styles.depthScoreContent}>
          <Text style={styles.depthScoreLabel}>Depth Score</Text>
          <Text style={styles.depthScoreValue}>{depthScore}</Text>
        </View>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <CircularProgress percentage={74} color="#ff9800" label="Focus Time" />
        <CircularProgress percentage={83} color="#8bc34a" label="Retention" />
        <CircularProgress percentage={92} color="#2196f3" label="Total Books" />
      </View>
      <RecentReading />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dateText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginRight: 10,
  },
  chevron: {
    fontSize: 20,
    color: '#9e9e9e',
  },
  depthScoreCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  iconCircle: {
    width: 70,
    height: 70,
    borderRadius: 35,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  iconText: {
    fontSize: 36,
  },
  depthScoreContent: {
    flex: 1,
  },
  depthScoreLabel: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  depthScoreValue: {
    fontSize: 18,
    color: '#757575',
    marginTop: 4,
  },
  chevronRight: {
    fontSize: 20,
    color: '#9e9e9e',
    transform: [{ rotate: '-90deg' }],
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    justifyContent: 'space-around',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  progressContainer: {
    alignItems: 'center',
  },
  circleWrapper: {
    position: 'relative',
    marginBottom: 10,
  },
  percentageContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  percentageText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  labelContainer: {
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
  },
  labelText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
  },
});

export default HomeDashboard;
