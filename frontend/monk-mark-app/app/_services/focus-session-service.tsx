import { FocusSessionDto } from "../_model/dto/focus-session-dto";
import { API_BASE_URL } from '../_constants/api-constants';

export const FocusSessionService = {
    async getExistingFocusSession(payload: { userGuid: string }): Promise<FocusSessionDto | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/focus-sessions/get-by-criteria`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data && result.data.length > 0) {
                const session = result.data[0];
                return {
                    userGuid: session.user_guid,
                    focusSessionGuid: session.guid,
                    libraryHdrGuid: session.library_hdr_guid,
                    bookName: session.book_name || '',
                    coverImageUrl: session.cover_image_url || '',
                };
            }

            return null;
        } catch (error) {
            console.error('Error getting existing focus session:', error);
            throw error;
        }
    },

    async createFocusSession(payload: {
        userGuid: string;
        libraryHdrGuid: string;
        timeHrs?: number;
        timeSeconds?: number;
    }): Promise<FocusSessionDto> {
        try {
            const response = await fetch(`${API_BASE_URL}/focus-sessions/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    time_hrs: payload.timeHrs != null ? Math.abs(payload.timeHrs) : undefined,
                    time_seconds: payload.timeSeconds != null ? Math.abs(payload.timeSeconds) : undefined,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                const session = result.data;
                return {
                    userGuid: session.user_guid,
                    focusSessionGuid: session.guid,
                    libraryHdrGuid: session.library_hdr_guid,
                    bookName: '',
                    coverImageUrl: '',
                };
            } else {
                throw new Error(result.data?.message || 'Failed to create focus session');
            }
        } catch (error) {
            console.error('Error creating focus session:', error);
            throw error;
        }
    },
    async updateFocusSession(payload: {
        focusSessionGuid: string;
        userGuid?: string;
        libraryHdrGuid?: string;
        timeHrs?: number;
        timeSeconds?: number;
    }): Promise<FocusSessionDto> {
        try {
            const response = await fetch(`${API_BASE_URL}/focus-sessions/update/${payload.focusSessionGuid}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    time_hrs: payload.timeHrs != null ? Math.abs(payload.timeHrs) : undefined,
                    time_seconds: payload.timeSeconds != null ? Math.abs(payload.timeSeconds) : undefined,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                const session = result.data;
                return {
                    userGuid: session.user_guid,
                    focusSessionGuid: session.guid,
                    libraryHdrGuid: session.library_hdr_guid,
                    bookName: '',
                    coverImageUrl: '',
                };
            } else {
                throw new Error(result.data?.message || 'Failed to update focus session');
            }
        } catch (error) {
            console.error('Error updating focus session:', error);
            throw error;
        }
    },
};


