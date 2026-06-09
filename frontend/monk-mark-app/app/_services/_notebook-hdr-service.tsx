

import { API_BASE_URL } from '../_constants/api-constants';

export const NotebookHdrService = {
    async create(payload: {
        user_guid: string;
        library_hdr_guid?: string;
        name: string;
        running_no?:string;
        description?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/create`, {
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
                throw new Error(result.data?.message || 'Failed to create notebook header');
            }
        } catch (error) {
            console.error('Error creating notebook header:', error);
            throw error;
        }
    },

    async getByGuid(notebookHdrId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/get-by-guid/${notebookHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to get notebook header');
            }
        } catch (error) {
            console.error('Error getting notebook header:', error);
            throw error;
        }
    },

    async getAll(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/get-all`, {
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
                throw new Error(result.data?.message || 'Failed to get all notebook headers');
            }
        } catch (error) {
            console.error('Error getting all notebook headers:', error);
            throw error;
        }
    },

    async getByUser(userGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/get-by-user/${userGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to get notebook headers by user');
            }
        } catch (error) {
            console.error('Error getting notebook headers by user:', error);
            throw error;
        }
    },

    async getByLibrary(libraryHdrGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/get-by-library/${libraryHdrGuid}`, {
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
            } else if (result.data?.message === 'NOTEBOOK_HDR_BY_LIBRARY_NOT_FOUND') {
                // Return null when notebook not found
                return null;
            } else {
                throw new Error(result.data?.message || 'Failed to get notebook headers by library');
            }
        } catch (error) {
            console.error('Error getting notebook headers by library:', error);
            throw error;
        }
    },

    async update(notebookHdrId: string, payload: {
        user_guid?: string;
        library_hdr_guid?: string;
        notebook_name?: string;
        description?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/update/${notebookHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to update notebook header');
            }
        } catch (error) {
            console.error('Error updating notebook header:', error);
            throw error;
        }
    },

    async deleteByGuid(notebookHdrId: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/notebooks/delete-by-guid/${notebookHdrId}`, {
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
                throw new Error(result.data?.message || 'Failed to delete notebook header');
            }
        } catch (error) {
            console.error('Error deleting notebook header:', error);
            throw error;
        }
    },
};


