

import { API_BASE_URL } from '../_constants/api-constants';

export const NotebookContentService = {
    async create(payload: {
        notebook_hdr_guid: string;
        user_guid: string;
        library_hdr_guid?: string;
        focus_session_guid?: string;
        content_text?: string;
        image_url?: string;
        highlight_metadata?: any;
        sequence_no?: number;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/create`, {
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
                throw new Error(result.data?.message || 'Failed to create notebook content');
            }
        } catch (error) {
            console.error('Error creating notebook content:', error);
            throw error;
        }
    },

    async getByGuid(contentId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/get-by-guid/${contentId}`, {
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
                throw new Error(result.data?.message || 'Failed to get notebook content');
            }
        } catch (error) {
            console.error('Error getting notebook content:', error);
            throw error;
        }
    },

    async getAll(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/get-all`, {
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
                throw new Error(result.data?.message || 'Failed to get all notebook contents');
            }
        } catch (error) {
            console.error('Error getting all notebook contents:', error);
            throw error;
        }
    },

    async getByNotebookHdr(notebookHdrGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/get-by-notebook-hdr/${notebookHdrGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get notebook contents by header');
            }
        } catch (error) {
            console.error('Error getting notebook contents by header:', error);
            throw error;
        }
    },

    async getByUser(userGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/get-by-user/${userGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get notebook contents by user');
            }
        } catch (error) {
            console.error('Error getting notebook contents by user:', error);
            throw error;
        }
    },

    async update(contentId: string, payload: {
        user_guid?: string;
        notebook_hdr_guid?: string;
        library_hdr_guid?: string;
        focus_session_guid?: string;
        content_text?: string;
        image_url?: string;
        highlight_metadata?: any;
        sequence_no?: number;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/update/${contentId}`, {
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
                throw new Error(result.data?.message || 'Failed to update notebook content');
            }
        } catch (error) {
            console.error('Error updating notebook content:', error);
            throw error;
        }
    },

    async deleteByGuid(contentId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-contents/delete-by-guid/${contentId}`, {
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
                throw new Error(result.data?.message || 'Failed to delete notebook content');
            }
        } catch (error) {
            console.error('Error deleting notebook content:', error);
            throw error;
        }
    },
};


