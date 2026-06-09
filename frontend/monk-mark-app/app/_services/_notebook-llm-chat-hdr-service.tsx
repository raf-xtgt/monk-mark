import { API_BASE_URL } from '../_constants/api-constants';

export const NotebookLlmChatHdrService = {
    async create(payload: {
        user_guid: string;
        notebook_hdr_guid?: string;
        library_hdr_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/create`, {
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
                throw new Error(result.data?.message || 'Failed to create chat header');
            }
        } catch (error) {
            console.error('Error creating chat header:', error);
            throw error;
        }
    },

    async getByGuid(chatHdrId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/get-by-guid/${chatHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat header');
            }
        } catch (error) {
            console.error('Error getting chat header:', error);
            throw error;
        }
    },

    async getAll(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/get-all`, {
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
                throw new Error(result.data?.message || 'Failed to get all chat headers');
            }
        } catch (error) {
            console.error('Error getting all chat headers:', error);
            throw error;
        }
    },

    async getByUser(userGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/get-by-user/${userGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat headers by user');
            }
        } catch (error) {
            console.error('Error getting chat headers by user:', error);
            throw error;
        }
    },

    async getByNotebook(notebookHdrGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/get-by-notebook/${notebookHdrGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat headers by notebook');
            }
        } catch (error) {
            console.error('Error getting chat headers by notebook:', error);
            throw error;
        }
    },

    async getByLibrary(libraryHdrGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/get-by-library/${libraryHdrGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat headers by library');
            }
        } catch (error) {
            console.error('Error getting chat headers by library:', error);
            throw error;
        }
    },

    async update(chatHdrId: string, payload: {
        user_guid?: string;
        notebook_hdr_guid?: string;
        library_hdr_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/update/${chatHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to update chat header');
            }
        } catch (error) {
            console.error('Error updating chat header:', error);
            throw error;
        }
    },

    async deleteByGuid(chatHdrId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-hdrs/delete-by-guid/${chatHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to delete chat header');
            }
        } catch (error) {
            console.error('Error deleting chat header:', error);
            throw error;
        }
    },
};

