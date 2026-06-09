import React, { useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert, TouchableOpacity, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import NoteTakingPanel from './_note-taking-panel';
import NotebookBackground from './_notebook-background';
import NoteContentView from './_note-content-view';
import { useAppState } from '../../_state-controller/state-controller';
import { NotebookContentService } from '../../_services/_notebook-content-service';
import { NotebookContentFileLinkService } from '../../_services/_notebook-content-file-link-service';

interface NotebookViewProps {
  notebookGuid: string;
  notebookName: string;
  libraryHdrGuid: string;
  onBack: () => void;
}

const NotebookView: React.FC<NotebookViewProps> = ({
  notebookGuid,
  notebookName,
  libraryHdrGuid,
  onBack,
}) => {
  const {
    user,
    noteContentViewMetadata,
    setNoteContentViewMetadata,
  } = useAppState();

  // Load existing notes when component mounts or notebookGuid changes
  useEffect(() => {
    const loadNotes = async () => {
      if (!notebookGuid) {
        return;
      }

      try {
        const notebookContents = await NotebookContentService.getByNotebookHdr(notebookGuid);

        if (notebookContents && notebookContents.length > 0) {
          const loadedNotesPromises = notebookContents.map(async (content: any, index: number) => {
            let images = undefined;

            if (content.guid) {
              try {
                const attachments = await NotebookContentFileLinkService.getNotebookContentAttachments(content.guid);

                if (attachments && attachments.length > 0) {
                  images = attachments.map((attachment: any) => ({
                    uri: attachment.file_path,
                    highlights: attachment.highlight_metadata?.highlights || [],
                    asyncStorageKey: `attachment_${attachment.content_guid}_${Date.now()}`,
                  }));
                }
              } catch (error) {
                console.error(`Error loading attachments for content ${content.guid}:`, error);
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
          setNoteContentViewMetadata({
            notes: [],
            activeNoteIndex: null,
          });
        }
      } catch (error) {
        console.error('Error loading notes:', error);
        setNoteContentViewMetadata({
          notes: [],
          activeNoteIndex: null,
        });
      }
    };

    loadNotes();
  }, [notebookGuid]);

  const handleAddNote = async () => {
    if (!user || !notebookGuid) {
      Alert.alert('Error', 'User or notebook information is missing.');
      return;
    }

    try {
      const payload = {
        notebook_hdr_guid: notebookGuid,
        user_guid: user.guid,
        library_hdr_guid: libraryHdrGuid,
        focus_session_guid: '',
        content_text: '',
        sequence_no: noteContentViewMetadata.notes.length,
      };

      const result = await NotebookContentService.create(payload);

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

  const handleHighlightNote = () => {
    Alert.alert('Coming Soon', 'Highlight feature will be available soon!');
  };

  const handleCapturePhoto = () => {
    Alert.alert('Coming Soon', 'Camera feature will be available soon!');
  };

  const handleNoteCameraPress = (index: number) => {
    setNoteContentViewMetadata({
      ...noteContentViewMetadata,
      activeNoteIndex: index,
    });
    Alert.alert('Coming Soon', `Camera feature for note ${index + 1} will be available soon!`);
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

            if (noteToDiscard?.guid) {
              try {
                await NotebookContentService.deleteByGuid(noteToDiscard.guid);
              } catch (error) {
                console.error('Error deleting note from database:', error);
                Alert.alert('Error', 'Failed to delete note. Please try again.');
                return;
              }
            }

            const filteredNotes = noteContentViewMetadata.notes.filter(
              (note) => note.index !== index
            );

            const reindexedNotes = filteredNotes.map((note, idx) => ({
              ...note,
              index: idx,
            }));

            let newActiveIndex = noteContentViewMetadata.activeNoteIndex;
            if (newActiveIndex === index) {
              newActiveIndex = null;
            } else if (newActiveIndex !== null && newActiveIndex > index) {
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

  const sortedNotes = [...noteContentViewMetadata.notes].sort(
    (a, b) => a.index - b.index
  );

  return (
    <View style={styles.container}>
      <NotebookBackground />

      {/* Header with back button and notebook name */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <View style={styles.titleContainer}>
          <Text style={styles.titleText} numberOfLines={1}>
            {notebookName}
          </Text>
        </View>
        <View style={styles.rightSpacer} />
      </View>

      <View style={styles.topRightPanel}>
        <NoteTakingPanel
          onAddNote={handleAddNote}
          onSaveNote={handleSaveNote}
          onHighlightNote={handleHighlightNote}
          onCapturePhoto={handleCapturePhoto}
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
            onCameraPress={() => handleNoteCameraPress(note.index)}
          />
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  titleContainer: {
    flex: 1,
    alignItems: 'center',
  },
  titleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  rightSpacer: {
    width: 40,
  },
  topRightPanel: {
    position: 'absolute',
    top: 70,
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

export default NotebookView;
