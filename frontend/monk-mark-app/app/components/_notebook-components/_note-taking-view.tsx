import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert, ActivityIndicator, Text, Modal } from 'react-native';
import NoteTakingTimer from './_note-taking-timer';
import NoteTakingPanel from './_note-taking-panel';
import NotebookBackground from './_notebook-background';
import NoteContentView from './_note-content-view';
import NoteContentCamera from './_note-content-camera';
import { useAppState } from '../../_state-controller/state-controller';
import { NotebookContentService } from '../../_services/_notebook-content-service';
import { NotebookContentFileLinkService } from '../../_services/_notebook-content-file-link-service';
import NotebookVoiceChatView from './_notebook-llm-components/_notebook-voice-chat-view';

const NoteTakingView: React.FC = () => {
  const {
    focusSession,
    user,
    noteContentViewMetadata,
    setNoteContentViewMetadata,
    currentNotebookGuid,
  } = useAppState();

  const [isLoading, setIsLoading] = useState(true);
  const [showCamera, setShowCamera] = useState(false);

  // Load existing notes when component mounts or currentNotebookGuid changes
  useEffect(() => {
    const loadNotes = async () => {
      if (!currentNotebookGuid) {
        console.log('No notebook guid available');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);

      try {
        const notebookContents = await NotebookContentService.getByNotebookHdr(currentNotebookGuid);

        if (notebookContents && notebookContents.length > 0) {
          // Transform API response to match noteContentViewMetadata structure
          const loadedNotesPromises = notebookContents.map(async (content: any, index: number) => {
            let images = undefined;

            // Fetch attachments for this notebook content
            if (content.guid) {
              try {
                const attachments = await NotebookContentFileLinkService.getNotebookContentAttachments(content.guid);

                if (attachments && attachments.length > 0) {
                  // Map attachments to the images format expected by noteContentViewMetadata
                  images = attachments.map((attachment: any) => ({
                    uri: attachment.file_path,
                    highlights: attachment.highlight_metadata?.highlights || [],
                    asyncStorageKey: `attachment_${attachment.content_guid}_${Date.now()}`,
                  }));
                }
              } catch (error) {
                console.error(`Error loading attachments for content ${content.guid}:`, error);
                // Continue without attachments if fetch fails
              }
            }

            return {
              index: index,
              guid: content.guid,
              content: content.content_text || '',
              isNew: false,
              images: images,
            };
          });

          const loadedNotes = await Promise.all(loadedNotesPromises);

          setNoteContentViewMetadata({
            notes: loadedNotes,
            activeNoteIndex: null,
          });
        } else {
          // No existing notes, start with empty state
          setNoteContentViewMetadata({
            notes: [],
            activeNoteIndex: null,
          });
        }
      } catch (error) {
        console.error('Error loading notes:', error);
        // Start with empty state on error
        setNoteContentViewMetadata({
          notes: [],
          activeNoteIndex: null,
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadNotes();
  }, [currentNotebookGuid]);

  const handleAddNote = async () => {
    if (!focusSession || !user || !currentNotebookGuid) {
      Alert.alert('Error', 'Session, user, or notebook information is missing.');
      return;
    }

    try {
      // Create empty note record in database immediately
      const payload = {
        notebook_hdr_guid: currentNotebookGuid,
        user_guid: user.guid,
        library_hdr_guid: focusSession.libraryHdrGuid,
        focus_session_guid: focusSession.focusSessionGuid,
        content_text: '',
        sequence_no: noteContentViewMetadata.notes.length,
      };

      const result = await NotebookContentService.create(payload);

      // Add new note with guid from database
      const newNote = {
        index: noteContentViewMetadata.notes.length,
        guid: result.guid,
        content: '',
        isNew: false,
      };

      setNoteContentViewMetadata({
        notes: [...noteContentViewMetadata.notes, newNote],
        activeNoteIndex: newNote.index,
      });

      // Open camera immediately after creating the note
      setShowCamera(true);
    } catch (error) {
      console.error('Error creating note:', error);
      Alert.alert('Error', 'Failed to create note. Please try again.');
    }
  };

  const handleSaveNote = async () => {
    if (noteContentViewMetadata.activeNoteIndex === null) {
      Alert.alert('No Active Note', 'Please select a note to save.');
      return;
    }

    const activeNote = noteContentViewMetadata.notes.find(
      (note) => note.index === noteContentViewMetadata.activeNoteIndex
    );

    if (!activeNote) {
      Alert.alert('Error', 'Active note not found.');
      return;
    }

    if (!activeNote.content.trim()) {
      Alert.alert('Empty Note', 'Please add some content before saving.');
      return;
    }

    if (!activeNote.guid) {
      Alert.alert('Error', 'Note ID is missing.');
      return;
    }

    try {
      // Update existing note
      const payload = {
        content_text: activeNote.content,
        sequence_no: activeNote.index,
      };

      await NotebookContentService.update(activeNote.guid, payload);
      Alert.alert('Success', 'Note updated successfully!');
    } catch (error) {
      console.error('Error saving note:', error);
      Alert.alert('Error', 'Failed to save note. Please try again.');
    }
  };

  const handleNotePress = (index: number) => {
    setNoteContentViewMetadata({
      ...noteContentViewMetadata,
      activeNoteIndex: index,
    });
  };

  const handleContentChange = (index: number, text: string) => {
    const updatedNotes = noteContentViewMetadata.notes.map((note) =>
      note.index === index ? { ...note, content: text } : note
    );

    setNoteContentViewMetadata({
      ...noteContentViewMetadata,
      notes: updatedNotes,
    });
  };

  const handleDiscard = (index: number) => {
    Alert.alert(
      'Discard Note',
      'Are you sure you want to discard this note?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Discard',
          style: 'destructive',
          onPress: async () => {
            const noteToDiscard = noteContentViewMetadata.notes.find(
              (note) => note.index === index
            );

            // Delete from database if note has a guid
            if (noteToDiscard?.guid) {
              try {
                await NotebookContentService.deleteByGuid(noteToDiscard.guid);
              } catch (error) {
                console.error('Error deleting note from database:', error);
                Alert.alert('Error', 'Failed to delete note. Please try again.');
                return;
              }
            }

            // Remove the note from state
            const filteredNotes = noteContentViewMetadata.notes.filter(
              (note) => note.index !== index
            );

            // Reindex remaining notes
            const reindexedNotes = filteredNotes.map((note, idx) => ({
              ...note,
              index: idx,
            }));

            // Update active index if needed
            let newActiveIndex = noteContentViewMetadata.activeNoteIndex;
            if (newActiveIndex === index) {
              newActiveIndex = null;
            } else if (
              newActiveIndex !== null &&
              newActiveIndex > index
            ) {
              newActiveIndex--;
            }

            setNoteContentViewMetadata({
              notes: reindexedNotes,
              activeNoteIndex: newActiveIndex,
            });
          },
        },
      ]
    );
  };

  // Sort notes by index in descending order (latest first)
  const sortedNotes = [...noteContentViewMetadata.notes].sort(
    (a, b) => b.index - a.index
  );

  if (isLoading) {
    return (
      <View style={styles.container}>
        <NotebookBackground />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6200ee" />
          <Text style={styles.loadingText}>Loading notes...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <NotebookBackground />

      <NoteTakingTimer />

      <View style={styles.topRightPanel}>
        <NoteTakingPanel
          onAddNote={handleAddNote}
          onSaveNote={handleSaveNote}
        />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
      >
        {sortedNotes.map((note) => (
          <NoteContentView
            key={note.index}
            index={note.index}
            content={note.content}
            isActive={noteContentViewMetadata.activeNoteIndex === note.index}
            onPress={() => handleNotePress(note.index)}
            onContentChange={(text) => handleContentChange(note.index, text)}
            onDiscard={() => handleDiscard(note.index)}
          />
        ))}
      </ScrollView>

      <NotebookVoiceChatView />

      {/* Camera Modal — opened after adding a new note */}
      <Modal
        visible={showCamera}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <NoteContentCamera onClose={() => setShowCamera(false)} />
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {
    fontSize: 15,
    color: '#666666',
    fontWeight: '500',
  },
  topRightPanel: {
    position: 'absolute',
    top: 12,
    right: 8,
    zIndex: 10,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingTop: 80,
    paddingBottom: 100,
  },
});

export default NoteTakingView;
