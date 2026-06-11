

import { API_BASE_URL } from '../_constants/api-constants';

export const GitLabSyncLogService = {

    async create(payload: {
        user_guid?: string;
        focus_session_guid?: string;
        notebook_hdr_guid?: string;
        library_hdr_guid?: string;
        llm_chat_hdr_guid?: string;
        reward_line_guid?: string;
        branch_name?: string;
        issue_url?: string;
        merge_request_url?: string;
        file_url?: string;
        sync_status?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to create gitlab sync log');
            }
        } catch (error) {
            console.error('Error creating gitlab sync log:', error);
            throw error;
        }
    },

    async getByGuid(guid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/get-by-guid/${guid}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to get gitlab sync log');
            }
        } catch (error) {
            console.error('Error getting gitlab sync log:', error);
            throw error;
        }
    },

    async getAll(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/get-all`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to get all gitlab sync logs');
            }
        } catch (error) {
            console.error('Error getting all gitlab sync logs:', error);
            throw error;
        }
    },

    async getByUser(userGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/get-by-user/${userGuid}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to get gitlab sync logs by user');
            }
        } catch (error) {
            console.error('Error getting gitlab sync logs by user:', error);
            throw error;
        }
    },

    async update(guid: string, payload: {
        user_guid?: string;
        focus_session_guid?: string;
        notebook_hdr_guid?: string;
        library_hdr_guid?: string;
        llm_chat_hdr_guid?: string;
        branch_name?: string;
        issue_url?: string;
        merge_request_url?: string;
        sync_status?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/update/${guid}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to update gitlab sync log');
            }
        } catch (error) {
            console.error('Error updating gitlab sync log:', error);
            throw error;
        }
    },

    async deleteByGuid(guid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/delete-by-guid/${guid}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to delete gitlab sync log');
            }
        } catch (error) {
            console.error('Error deleting gitlab sync log:', error);
            throw error;
        }
    },

    async getContext(payload: {
        user_guid: string;
        library_hdr_guid?: string;
        notebook_hdr_guid?: string;
        llm_chat_hdr_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/gitlab-sync-logs/context`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE') {
                return result.data;
            } else {
                throw new Error(result.data?.message || 'Failed to get gitlab context');
            }
        } catch (error) {
            console.error('Error getting gitlab context:', error);
            throw error;
        }
    },
};
