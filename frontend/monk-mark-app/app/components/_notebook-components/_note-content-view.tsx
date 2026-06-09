import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useAppState } from '../../_state-controller/state-controller';
import NoteContentCamera from './_note-content-camera';

interface NoteContentViewProps {
    index: number;
    content: string;
    isActive: boolean;
    onPress: () => void;
    onContentChange: (text: string) => void;
    onDiscard: () => void;
}

const NoteContentView: React.FC<NoteContentViewProps> = ({
    index,
    content,
    isActive,
    onPress,
    onContentChange,
    onDiscard,
}) => {
    const [showCamera, setShowCamera] = useState(false);
    const [showImagePreview, setShowImagePreview] = useState(false);
    const { noteContentViewMetadata, setNoteContentViewMetadata } = useAppState();

    const currentNote = noteContentViewMetadata.notes[index];
    const imageCount = currentNote?.images?.length || 0;

    const handleCameraPress = () => {
        // Set this note as active before opening camera
        setNoteContentViewMetadata({
            ...noteContentViewMetadata,
            activeNoteIndex: index,
        });
        setShowCamera(true);
    };

    const handleCloseCamera = () => {
        setShowCamera(false);
    };

    const handleAttachmentPress = () => {
        if (imageCount > 0) {
            setShowImagePreview(true);
        }
    };

    return (
        <>
            <View style={[styles.container, isActive && styles.activeContainer]}>
                {/* discard button - top right */}
                <TouchableOpacity
                    style={styles.discardButton}
                    onPress={onDiscard}
                    activeOpacity={0.7}
                >
                    <Ionicons name="close-circle" size={24} color="#ff6b6b" />
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.touchableArea}
                    onPress={onPress}
                    activeOpacity={1}
                >
                    {/* input area */}
                    <TextInput
                        style={styles.textInput}
                        multiline
                        placeholder="Start typing your note..."
                        placeholderTextColor="#999"
                        value={content}
                        onChangeText={onContentChange}
                        onFocus={onPress}
                        textAlignVertical="top"
                        scrollEnabled={false}
                    />
                </TouchableOpacity>

                {/* Bottom buttons container */}
                <View style={styles.bottomButtonsContainer}>
                    {/* Camera button */}
                    <TouchableOpacity
                        style={styles.cameraButton}
                        onPress={handleCameraPress}
                        activeOpacity={0.7}
                    >
                        <Ionicons name="camera" size={20} color="#666" />
                    </TouchableOpacity>

                    {/* Attachment button with count */}
                    {imageCount > 0 && (
                        <TouchableOpacity
                            style={styles.attachmentButton}
                            onPress={handleAttachmentPress}
                            activeOpacity={0.7}
                        >
                            <Ionicons name="attach" size={20} color="#666" />
                            <View style={styles.countBadge}>
                                <Text style={styles.countText}>{imageCount}</Text>
                            </View>
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            {/* Camera Modal */}
            <Modal
                visible={showCamera}
                animationType="slide"
                presentationStyle="fullScreen"
            >
                <NoteContentCamera onClose={handleCloseCamera} />
            </Modal>

            {/* Image Preview Modal */}
            <Modal
                visible={showImagePreview}
                animationType="fade"
                transparent
                onRequestClose={() => setShowImagePreview(false)}
            >
                <View style={styles.previewModalContainer}>
                    <TouchableOpacity
                        style={styles.previewCloseButton}
                        onPress={() => setShowImagePreview(false)}
                    >
                        <Ionicons name="close" size={32} color="#fff" />
                    </TouchableOpacity>
                    {currentNote?.images?.map((image, idx) => (
                        <View key={idx} style={styles.previewImageContainer}>
                            <Image source={{ uri: image.uri }} style={styles.previewImage} contentFit="contain" />
                            {image.highlights.map((highlight, hIdx) => (
                                <View
                                    key={hIdx}
                                    style={[
                                        styles.previewHighlight,
                                        {
                                            left: highlight.x,
                                            top: highlight.y,
                                            width: highlight.width,
                                            height: highlight.height,
                                        },
                                    ]}
                                />
                            ))}
                        </View>
                    ))}
                </View>
            </Modal>
        </>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#fffacd',
        borderRadius: 8,
        padding: 16,
        paddingBottom: 40,
        marginBottom: 16,
        marginHorizontal: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
        opacity: 0.85,
        position: 'relative',
    },
    activeContainer: {
        opacity: 1,
        borderWidth: 2,
        borderColor: '#4FC3F7',
    },
    touchableArea: {
        width: '100%',
    },
    textInput: {
        fontSize: 16,
        color: '#333',
        lineHeight: 24,
        minHeight: 60,
        paddingTop: 0,
        paddingBottom: 50,
    },
    bottomButtonsContainer: {
        position: 'absolute',
        bottom: 8,
        left: 8,
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    cameraButton: {
        backgroundColor: '#fff',
        borderRadius: 20,
        padding: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 2,
        elevation: 2,
    },
    attachmentButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 16,
        padding: 6,
        paddingRight: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 2,
        elevation: 2,
    },
    countBadge: {
        backgroundColor: '#4FC3F7',
        borderRadius: 10,
        minWidth: 20,
        height: 20,
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: 4,
        paddingHorizontal: 6,
    },
    countText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
    },
    discardButton: {
        position: 'absolute',
        top: 8,
        right: 8,
    },
    previewModalContainer: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.9)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    previewCloseButton: {
        position: 'absolute',
        top: 40,
        right: 20,
        zIndex: 10,
        backgroundColor: 'rgba(0,0,0,0.5)',
        borderRadius: 20,
        padding: 8,
    },
    previewImageContainer: {
        width: '90%',
        height: '70%',
        position: 'relative',
        marginBottom: 20,
    },
    previewImage: {
        width: '100%',
        height: '100%',
    },
    previewHighlight: {
        position: 'absolute',
        backgroundColor: 'rgba(173, 255, 47, 0.3)',
        borderWidth: 2,
        borderColor: 'rgba(173, 255, 47, 0.8)',
    },
});

export default NoteContentView;
