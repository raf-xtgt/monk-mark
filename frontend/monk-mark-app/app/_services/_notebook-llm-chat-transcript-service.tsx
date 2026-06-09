
import { API_BASE_URL } from '../_constants/api-constants';

export const NotebookLlmChatTranscriptService = {
    async create(payload: {
        user_guid: string;
        llm_chat_hdr_guid: string;
        msg_content: string;
        sender: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/create`, {
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
                throw new Error(result.data?.message || 'Failed to create chat transcript');
            }
        } catch (error) {
            console.error('Error creating chat transcript:', error);
            throw error;
        }
    },

    async getByGuid(transcriptId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/get-by-guid/${transcriptId}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat transcript');
            }
        } catch (error) {
            console.error('Error getting chat transcript:', error);
            throw error;
        }
    },

    async getAll(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/get-all`, {
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
                throw new Error(result.data?.message || 'Failed to get all chat transcripts');
            }
        } catch (error) {
            console.error('Error getting all chat transcripts:', error);
            throw error;
        }
    },

    async getByUser(userGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/get-by-user/${userGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat transcripts by user');
            }
        } catch (error) {
            console.error('Error getting chat transcripts by user:', error);
            throw error;
        }
    },

    async getByChatHdr(llmChatHdrGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/get-by-chat-hdr/${llmChatHdrGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get chat transcripts by chat header');
            }
        } catch (error) {
            console.error('Error getting chat transcripts by chat header:', error);
            throw error;
        }
    },

    async getByNotebookHdr(payload: {
        notebook_hdr_guid: string;
        user_guid: string;
        library_hdr_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/get-by-notebook-hdr`, {
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
                throw new Error(result.data?.message || 'Failed to get chat transcripts by notebook');
            }
        } catch (error) {
            console.error('Error getting chat transcripts by notebook:', error);
            throw error;
        }
    },

    async update(transcriptId: string, payload: {
        user_guid?: string;
        llm_chat_hdr_guid?: string;
        msg_content?: string;
        sender?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/update/${transcriptId}`, {
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
                throw new Error(result.data?.message || 'Failed to update chat transcript');
            }
        } catch (error) {
            console.error('Error updating chat transcript:', error);
            throw error;
        }
    },

    async deleteByGuid(transcriptId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/delete-by-guid/${transcriptId}`, {
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
                throw new Error(result.data?.message || 'Failed to delete chat transcript');
            }
        } catch (error) {
            console.error('Error deleting chat transcript:', error);
            throw error;
        }
    },

    async countByNotebook(notebookHdrGuid: string): Promise<{ notebook_hdr_guid: string; total_count: number }> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/count-by-notebook/${notebookHdrGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get transcript count by notebook');
            }
        } catch (error) {
            console.error('Error getting transcript count by notebook:', error);
            throw error;
        }
    },

    async generateGreeting(payload: {
        notebook_hdr_guid: string;
        user_guid: string;
        library_hdr_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebook-llm-chat-transcripts/generate-greeting`, {
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
                throw new Error(result.data?.message || 'Failed to generate greeting');
            }
        } catch (error) {
            console.error('Error generating greeting:', error);
            throw error;
        }
    },
};