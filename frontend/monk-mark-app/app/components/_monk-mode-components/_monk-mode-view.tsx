import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import FocusTimer from './_focus-timer';
import ProgressAura from './_monk-mode-progress-aura';
import MonkModeRewardDialogue from './_monk-mode-reward-dialog';
import { useAppState } from '../../_state-controller/state-controller';
import { FocusSessionService } from '../../_services/focus-session-service';
import { LibraryService } from '../../_services/library-service';
import { NotebookHdrService } from '../../_services/_notebook-hdr-service';
import { RewardHdrService } from '../../_services/_reward-hdr-service';
import { RewardLineService } from '../../_services/_reward-line-service';
import { AgentTriggerService } from '../../_services/_agent-trigger-service';
import { NotebookLlmChatTranscriptService } from '../../_services/_notebook-llm-chat-transcript-service';
import { MilestoneEvaluation } from '../../_model/dto/reward-output-dto';
import { Ionicons } from '@expo/vector-icons';
import MonkModeProgressRemarks from './_monk-mode-progress';
import MonkModeEvaluationStatus from './_monk-mode-evaluation-status';

interface BookResult {
  guid: string;
  book_name: string;
  author_name: string;
  description: string;
  cover_image_url: string;
}

interface MonkModeViewProps {
  selectedBook: BookResult | null;
}

const MonkModeView: React.FC<MonkModeViewProps> = ({ selectedBook }) => {
  const [currentHours, setCurrentHours] = useState(0);
  const [currentMinutes, setCurrentMinutes] = useState(0);
  const [currentSeconds, setCurrentSeconds] = useState(0);
  const [initialTimeSeconds, setInitialTimeSeconds] = useState(0);
  const [evaluationStatus, setEvaluationStatus] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [milestoneData, setMilestoneData] = useState<MilestoneEvaluation | null>(null);
  const [rewardDialogVisible, setRewardDialogVisible] = useState(false);
  const [rewardImageUrl, setRewardImageUrl] = useState<string | null>(null);

  const {
    focusSession,
    setFocusSession,
    setShowTopBar,
    setShowBottomNavigation,
    setCurrentRoute,
    focusSessionMetadata,
    setFocusSessionMetadata,
    user,
    setCurrentNotebookGuid,
    setFocusSessionCompleted
  } = useAppState();

  // Get isRunning from global state
  const isRunning = focusSessionMetadata?.isRunning ?? false;

  if (!selectedBook) {
    return null;
  }

  const handleTimeUpdate = (hours: number, minutes: number, seconds: number) => {
    setCurrentHours(hours);
    setCurrentMinutes(minutes);
    setCurrentSeconds(seconds);

    // Detect timer running out to zero
    if (hours === 0 && minutes === 0 && seconds === 0 && isRunning) {
      handleSessionComplete();
    }
  };

  const handleSessionComplete = async () => {
    setFocusSessionCompleted(true);

    // Show UI message
    // Alert.alert('Session Complete', 'Your focus session has ended.');
    // console.log("session completed")
    // Stop the timer and clean up
    setFocusSessionMetadata(null);
    setShowTopBar(false);
    setShowBottomNavigation(true);

    // Persist elapsed time if we have a session
    if (focusSession?.focusSessionGuid) {
      try {
        await FocusSessionService.updateFocusSession({
          focusSessionGuid: focusSession.focusSessionGuid,
          timeHrs: initialTimeSeconds / 3600,
          timeSeconds: initialTimeSeconds,
        });
      } catch (error) {
        console.error('Error updating focus session on timer expiry:', error);
      }
    }

    // Run session evaluation
    await handleSessionEvaluation();
  };

  const handlePlay = async () => {
    if (!focusSession || !user?.guid) return;

    try {
      // Calculate initial time in seconds
      const totalSeconds = currentHours * 3600 + currentMinutes * 60 + currentSeconds;
      setInitialTimeSeconds(totalSeconds);

      // Update last_read in library record
      await LibraryService.updateLastReadLibraryBookRecord(focusSession.libraryHdrGuid);

      // Create focus session in database
      const createdSession = await FocusSessionService.createFocusSession({
        userGuid: user.guid,
        libraryHdrGuid: focusSession.libraryHdrGuid,
        timeHrs: currentHours + currentMinutes / 60,
        timeSeconds: totalSeconds,
      });

      // Update focus session with the created guid
      setFocusSession({
        ...focusSession,
        focusSessionGuid: createdSession.focusSessionGuid,
      });

      // Update metadata with running state and book info
      setFocusSessionMetadata({
        bookName: selectedBook.book_name,
        coverImageUrl: selectedBook.cover_image_url,
        isRunning: true,
      });

      // Hide top and bottom bars
      setShowTopBar(false);
      setShowBottomNavigation(false);

      // Pre-generate initial greeting for the voice chat if no transcripts exist yet.
      // This ensures the greeting is ready by the time the user navigates to the voice chat.
      await ensureInitialGreeting();
    } catch (error) {
      console.error('Error starting focus session:', error);
    }
  };

  /**
   * Ensure an initial greeting exists for the voice chat transcript.
   * Resolves the notebook GUID, checks transcript count, and generates
   * a greeting if no transcripts exist yet.
   */
  const ensureInitialGreeting = async () => {
    if (!focusSession?.libraryHdrGuid || !user?.guid) return;

    try {
      // Resolve notebook GUID for this library
      const notebook = await NotebookHdrService.getByLibrary(focusSession.libraryHdrGuid);

      let notebookGuid: string;

      if (notebook) {
        notebookGuid = notebook.guid;
      } else {
        // No notebook exists yet — create one
        const newNotebook = await NotebookHdrService.create({
          user_guid: user.guid,
          library_hdr_guid: focusSession.libraryHdrGuid,
          name: `${focusSession.bookName} - Notes`,
          running_no: "test-running-no",
          description: `Notes for ${focusSession.bookName}`,
        });
        notebookGuid = newNotebook.guid;
      }

      // Store notebook guid in state so voice chat can use it
      setCurrentNotebookGuid(notebookGuid);

      // Check if transcripts already exist for this notebook
      const countResult = await NotebookLlmChatTranscriptService.countByNotebook(notebookGuid);
      const totalCount = countResult?.total_count;

      if (!totalCount) {
        // No transcripts exist — generate an initial greeting
        await NotebookLlmChatTranscriptService.generateGreeting({
          notebook_hdr_guid: notebookGuid,
          user_guid: user.guid,
          library_hdr_guid: focusSession.libraryHdrGuid,
        });
        console.log('Pre-generated initial greeting for voice chat');
      }
    } catch (error) {
      console.error('Error ensuring initial greeting:', error);
    }
  };

  const handlePause = () => {
    setFocusSessionMetadata({
      ...focusSessionMetadata,
      bookName: focusSessionMetadata?.bookName ?? selectedBook.book_name,
      coverImageUrl: focusSessionMetadata?.coverImageUrl ?? selectedBook.cover_image_url,
      isRunning: false,
    });
    setShowTopBar(true);
    setShowBottomNavigation(true);
  };

  const handleStop = async () => {
    if (!focusSession?.focusSessionGuid) return;

    // Alert.alert('Session stopped', 'Your focus session has ended.');
    // console.log("session stopped")

    try {
      // Calculate elapsed time
      const remainingSeconds = currentHours * 3600 + currentMinutes * 60 + currentSeconds;
      const elapsedSeconds = initialTimeSeconds - remainingSeconds;
      const elapsedHours = elapsedSeconds / 3600;

      // Update focus session in database
      await FocusSessionService.updateFocusSession({
        focusSessionGuid: focusSession.focusSessionGuid,
        timeHrs: elapsedHours,
        timeSeconds: elapsedSeconds,
      });

      // Mark session as completed
      setFocusSessionCompleted(true);

      // Stop timer and clear metadata
      setFocusSessionMetadata(null);

      // Show top and bottom bars
      setShowTopBar(false);
      setShowBottomNavigation(true);
    } catch (error) {
      console.error('Error stopping focus session:', error);
    }

    // Run session evaluation
    await handleSessionEvaluation();
  };

  const handleNoteTaking = async () => {
    if (!focusSession?.libraryHdrGuid || !focusSession?.userGuid) {
      console.error('Missing required focus session data');
      return;
    }

    try {
      // Check if notebook exists for this library
      const notebook = await NotebookHdrService.getByLibrary(focusSession.libraryHdrGuid);

      let notebookGuid: string;

      if (notebook) {
        // Notebook found, use its guid
        notebookGuid = notebook.guid;
      } else {
        // No notebook found, create a new one
        const newNotebook = await NotebookHdrService.create({
          user_guid: focusSession.userGuid,
          library_hdr_guid: focusSession.libraryHdrGuid,
          name: `${focusSession.bookName} - Notes`,
          running_no: "test-running-no",
          description: `Notes for ${focusSession.bookName}`,
        });
        notebookGuid = newNotebook.guid;
      }

      // Store the notebook guid in state
      setCurrentNotebookGuid(notebookGuid);

      // Navigate to note taker
      setCurrentRoute(6);
    } catch (error) {
      console.error('Error handling notebook:', error);
      // Still navigate even if there's an error
      setCurrentRoute(6);
    }
  };


  // Retrieve current reward status on mount and periodically while timer is running
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasFetchedInitialRef = useRef(false);

  const retrieveCurrentRewardStatus = useCallback(async () => {
    if (!user?.guid || !focusSession?.libraryHdrGuid) return;

    try {
      const summary = await RewardHdrService.getRewardSummaryByLibrary(
        user.guid,
        focusSession.libraryHdrGuid,
      );
      const evaluated = await RewardHdrService.evaluateRewardMilestone(summary);
      const milestone = evaluated.milestone_evaluation;
      if (milestone) {
        setMilestoneData(milestone);
      }
    } catch (error) {
      console.error('Error retrieving current reward status:', error);
    }
  }, [user?.guid, focusSession?.libraryHdrGuid]);

  // Fetch on mount (when user arrives at MonkModeView with a selected book)
  useEffect(() => {
    if (user?.guid && focusSession?.libraryHdrGuid && !hasFetchedInitialRef.current) {
      hasFetchedInitialRef.current = true;
      retrieveCurrentRewardStatus();
    }
  }, [user?.guid, focusSession?.libraryHdrGuid, retrieveCurrentRewardStatus]);

  // Poll every 15 minutes while the timer is running
  useEffect(() => {
    if (isRunning) {
      pollingIntervalRef.current = setInterval(() => {
        retrieveCurrentRewardStatus();
      }, 15 * 60 * 1000); // 15 minutes
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [isRunning, retrieveCurrentRewardStatus]);




  //  Session evaluation: called after stop or timer expiry
  const handleSessionEvaluation = async () => {
    if (!user?.guid || !focusSession?.libraryHdrGuid) {
      console.log('Missing user or library guid for evaluation');
      return;
    }

    setIsEvaluating(true);

    try {
      // Step 1: Fetch reward summary
      setEvaluationStatus('Fetching reading progress...');
      const summary = await RewardHdrService.getRewardSummaryByLibrary(
        user.guid,
        focusSession.libraryHdrGuid,
      );
      console.log('Reward summary fetched:', summary);

      // Step 2: Evaluate milestone
      setEvaluationStatus('Evaluating milestone progression...');
      const evaluated = await RewardHdrService.evaluateRewardMilestone(summary);
      console.log('Milestone evaluation result:', evaluated);

      // Step 2.5: Generate motivational quote
      try {
        setEvaluationStatus('Generating motivational insight...');
        const latestRewardHdrGuid = evaluated.reward_list.length > 0
          ? evaluated.reward_list[evaluated.reward_list.length - 1].guid
          : undefined;
        const quoteResponse = await AgentTriggerService.triggerMilestoneQuote({
          library_hdr_guid: focusSession.libraryHdrGuid,
          reward_hdr_guid: latestRewardHdrGuid,
        });
        if (quoteResponse.quote) {
          setEvaluationStatus(quoteResponse.quote);
        }
      } catch (quoteError) {
        console.warn('Failed to generate milestone quote:', quoteError);
      }

      // Step 3: Show result
      const milestone = evaluated.milestone_evaluation;
      if (milestone) {
        setMilestoneData(milestone);
      }

      // Step 4: Trigger art generation if milestone unlocked
      if (milestone && (milestone.agent_to_trigger === 'ART_GEN' || milestone.agent_to_trigger === 'ART_EVOLUTION')) {
        
        // TODO: trigger gitlab agent
        
        
        setEvaluationStatus('Generating Legacy Art...');
        const notebookGuid = focusSession?.libraryHdrGuid || '';
        const eventType = milestone.agent_to_trigger === 'ART_EVOLUTION' ? 'generate_art_evolution' : 'generate_art';
        const artResponse = await AgentTriggerService.triggerAgent({
          userGuid: user.guid,
          libraryHdrGuid: focusSession.libraryHdrGuid,
          notebookHdrGuid: notebookGuid,
          eventType: eventType,
        });
        console.log('Art generation response:', artResponse);
        setEvaluationStatus('Legacy Art generated!');

        // Step 5: Create reward line record with the generated art URL
        if (artResponse.storage_url && evaluated.reward_list.length > 0) {
          const rewardHdrGuid = evaluated.reward_list[evaluated.reward_list.length - 1].guid;
          await RewardLineService.createRewardLine({
            userGuid: user.guid,
            rewardHdrGuid: rewardHdrGuid,
            imageUrl: artResponse.storage_url,
            tierLevel: milestone.current_tier,
          });
          console.log('Reward line created for tier:', milestone.current_tier);
        }

        // Show reward dialog with the generated art
        if (artResponse.storage_url) {
          setRewardImageUrl(artResponse.storage_url);
          setRewardDialogVisible(true);
        }
      }

    } catch (error) {
      console.error('Error during session evaluation:', error);
      setEvaluationStatus('Evaluation failed.');
    } finally {
      setIsEvaluating(false);
    }
  };


  return (
    <View style={styles.container}>
      <FocusTimer isRunning={isRunning} onTimeUpdate={handleTimeUpdate} />

      <View style={styles.bookSection}>
        {/* Book Image wrapped in Progress Aura */}
        <ProgressAura milestone={milestoneData}>
          <Image
            source={{ uri: selectedBook.cover_image_url }}
            style={styles.bookCover}
            resizeMode="cover"
          />
        </ProgressAura>

        {/* Focus timer control buttons */}
        <View style={styles.controlButtons}>
          {!isRunning ? (
            // play button
            <TouchableOpacity style={styles.playButton} onPress={handlePlay}>
              <Ionicons name="play" size={32} color="white" />
            </TouchableOpacity>
          ) : (
            <>
              {/* pause button */}
              <TouchableOpacity style={styles.pauseButton} onPress={handlePause}>
                <Ionicons name="pause" size={32} color="white" />
              </TouchableOpacity>

              {/* stop button */}
              <TouchableOpacity style={styles.stopButton} onPress={handleStop}>
                <Ionicons name="stop" size={32} color="white" />
              </TouchableOpacity>

              {/* note taking button */}
              <TouchableOpacity style={styles.noteButton} onPress={handleNoteTaking}>
                <Ionicons name="create-outline" size={32} color="white" />
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>

      {/* Reward Dialog to show the image*/}
      <MonkModeRewardDialogue
        visible={rewardDialogVisible}
        imageUrl={rewardImageUrl}
        onClose={() => setRewardDialogVisible(false)}
        onGalleryPress={() => {}}
      />

      {/* Monk mode progress remarks */}
      <MonkModeProgressRemarks milestone={milestoneData} />
    
      {/* monk mode evaluation */}
      <MonkModeEvaluationStatus
        isEvaluating={isEvaluating}
        statusMessage={evaluationStatus}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#4a4a5e',
  },
  bookSection: {
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  bookCover: {
    width: 120,
    height: 160,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  bookInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.7,
    marginBottom: 8,
  },
  bookName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  author: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.8,
  },
  controlButtons: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 10,
  },
  playButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#4ecdc4',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  pauseButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#f4c542',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  stopButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#ff6b9d',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  noteButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#9b59b6',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  buttonText: {
    fontSize: 28,
    color: '#ffffff',
  },
});

export default MonkModeView;
