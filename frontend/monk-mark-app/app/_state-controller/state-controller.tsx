import React, { createContext, useContext, useState, useRef, useCallback, ReactNode } from 'react';
import { UserStateDto } from '../_model/dto/user-state-dto';
import { FocusSessionDto } from '../_model/dto/focus-session-dto';
import { TranscriptMessage } from '../_model/dto/llm-dto/llm-dto';

interface AppState {
    showTopBar: boolean;
    showBottomNavigation: boolean;
    user: UserStateDto | null;
    currentRoute: number;
    focusSession: FocusSessionDto | null;
    notesTaken: string[];
    focusTimer: { hours: number; minutes: number; seconds: number } | null;
    focusSessionMetadata: { bookName: string; coverImageUrl: string; isRunning: boolean } | null;
    noteContentViewMetadata: {
        notes: Array<{
            index: number;
            guid?: string;
            content: string;
            isNew: boolean;
            images?: Array<{
                uri: string;
                highlights: Array<{ x: number; y: number; width: number; height: number }>;
                asyncStorageKey: string;
            }>;
        }>;
        activeNoteIndex: number | null;
    };
    currentNotebookGuid: string | null;
    notebookLlmChatGuid: string | null;
    notebookChatTranscript: TranscriptMessage[];
    focusSessionCompleted: boolean;
    setShowTopBar: (show: boolean) => void;
    setShowBottomNavigation: (show: boolean) => void;
    setUser: (user: UserStateDto | null) => void;
    setCurrentRoute: (route: number) => void;
    setFocusSession: (focusSession: FocusSessionDto | null) => void;
    setNotesTaken: (notes: string[]) => void;
    setFocusTimer: (timer: { hours: number; minutes: number; seconds: number } | null | ((prev: { hours: number; minutes: number; seconds: number } | null) => { hours: number; minutes: number; seconds: number } | null)) => void;
    setFocusSessionMetadata: (metadata: { bookName: string; coverImageUrl: string; isRunning: boolean } | null) => void;
    setNoteContentViewMetadata: (metadata: {
        notes: Array<{
            index: number;
            guid?: string;
            content: string;
            isNew: boolean;
            images?: Array<{
                uri: string;
                highlights: Array<{ x: number; y: number; width: number; height: number }>;
                asyncStorageKey: string;
            }>;
        }>;
        activeNoteIndex: number | null;
    }) => void;
    setCurrentNotebookGuid: (guid: string | null) => void;
    setNotebookLlmChatGuid: (guid: string | null) => void;
    setNotebookChatTranscript: (transcript: TranscriptMessage[] | ((prev: TranscriptMessage[]) => TranscriptMessage[])) => void;
    setFocusSessionCompleted: (completed: boolean) => void;
    registerVoiceChatCleanup: (cleanup: (() => Promise<void>) | null) => void;
    disconnectVoiceChat: () => Promise<void>;
}

const AppStateContext = createContext<AppState | undefined>(undefined);

export const useAppState = () => {
    const context = useContext(AppStateContext);
    if (!context) {
        throw new Error('useAppState must be used within AppStateProvider');
    }
    return context;
};

interface AppStateProviderProps {
    children: ReactNode;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ children }) => {
    const [showTopBar, setShowTopBar] = useState(false);
    const [showBottomNavigation, setShowBottomNavigation] = useState(true);
    const [user, setUser] = useState<UserStateDto | null>(null);
    const [currentRoute, setCurrentRoute] = useState(1);
    const [focusSession, setFocusSession] = useState<FocusSessionDto | null>(null);
    const [notesTaken, setNotesTaken] = useState<string[]>([]);
    const [focusTimer, setFocusTimer] = useState<{ hours: number; minutes: number; seconds: number } | null>(null);
    const [focusSessionMetadata, setFocusSessionMetadata] = useState<{ bookName: string; coverImageUrl: string; isRunning: boolean } | null>(null);
    const [noteContentViewMetadata, setNoteContentViewMetadata] = useState<{
        notes: Array<{
            index: number;
            guid?: string;
            content: string;
            isNew: boolean;
            images?: Array<{
                uri: string;
                highlights: Array<{ x: number; y: number; width: number; height: number }>;
                asyncStorageKey: string;
            }>;
        }>;
        activeNoteIndex: number | null;
    }>({ notes: [], activeNoteIndex: null });
    const [currentNotebookGuid, setCurrentNotebookGuid] = useState<string | null>(null);
    const [notebookLlmChatGuid, setNotebookLlmChatGuid] = useState<string | null>(null);
    const [notebookChatTranscript, setNotebookChatTranscript] = useState<TranscriptMessage[]>([]);
    const [focusSessionCompleted, setFocusSessionCompleted] = useState<boolean>(false);

    const voiceChatCleanupRef = useRef<(() => Promise<void>) | null>(null);

    const registerVoiceChatCleanup = useCallback((cleanup: (() => Promise<void>) | null) => {
        voiceChatCleanupRef.current = cleanup;
    }, []);

    const disconnectVoiceChat = useCallback(async () => {
        if (voiceChatCleanupRef.current) {
            await voiceChatCleanupRef.current();
        }
    }, []);

    const value: AppState = {
        showTopBar,
        showBottomNavigation,
        user,
        currentRoute,
        focusSession,
        notesTaken,
        focusTimer,
        focusSessionMetadata,
        noteContentViewMetadata,
        currentNotebookGuid,
        notebookLlmChatGuid,
        notebookChatTranscript,
        focusSessionCompleted,
        setShowTopBar,
        setShowBottomNavigation,
        setUser,
        setCurrentRoute,
        setFocusSession,
        setNotesTaken,
        setFocusTimer,
        setFocusSessionMetadata,
        setNoteContentViewMetadata,
        setCurrentNotebookGuid,
        setNotebookLlmChatGuid,
        setNotebookChatTranscript,
        setFocusSessionCompleted,
        registerVoiceChatCleanup,
        disconnectVoiceChat,
    };

    return (
        <AppStateContext.Provider value={value}>
            {children}
        </AppStateContext.Provider>
    );
};
