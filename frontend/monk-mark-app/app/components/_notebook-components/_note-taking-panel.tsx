import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NoteTakingPanelProps {
    onAddNote?: () => void;
    onSaveNote?: () => void;
}

const NoteTakingPanel: React.FC<NoteTakingPanelProps> = ({
    onAddNote,
    onSaveNote,
}) => {
    return (
        <View style={styles.container}>
            {/* add note button */}
            <TouchableOpacity
                style={styles.button}
                onPress={onAddNote}
                activeOpacity={0.7}
            >
                <Ionicons name="add" size={18} color="#333333" />
            </TouchableOpacity>

            {/* save note button */}
            <TouchableOpacity
                style={styles.button}
                onPress={onSaveNote}
                activeOpacity={0.7}
            >
                <Ionicons name="save" size={16} color="#333333" />
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        backgroundColor: '#4FC3F7',
        borderRadius: 18,
        paddingVertical: 6,
        paddingHorizontal: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
        elevation: 6,
        gap: 8,
    },
    button: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: '#E0E0E0',
        justifyContent: 'center',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.15,
        shadowRadius: 2,
        elevation: 3,
    },
});

export default NoteTakingPanel;
