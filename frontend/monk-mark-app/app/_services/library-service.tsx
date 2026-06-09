

import { API_BASE_URL } from '../_constants/api-constants';
import { BookSearchDto } from '../_model/dto/book-search-dto';

export const LibraryService = {
    async bookSearch(payload: BookSearchDto): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/librarys/search-book`, {
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
                throw new Error(result.data?.message || 'Failed to search book');
            }
        } catch (error) {
            console.error('Error searching book:', error);
            throw error;
        }
    },

    async updateLibraryBookRecord(libraryGuid: string, payload: {
        book_name?: string;
        book_desc?: string;
        last_read?: string;
        file_guid?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/librarys/update/${libraryGuid}`, {
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
                throw new Error(result.data?.message || 'Failed to update library record');
            }
        } catch (error) {
            console.error('Error updating library record:', error);
            throw error;
        }
    },

    async getLibraryBookRecordsByCriteria(payload: {
        guid?: string;
        user_guid?: string;
        book_name?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/librarys/get-by-criteria`, {
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
                throw new Error(result.data?.message || 'Failed to get library records');
            }
        } catch (error) {
            console.error('Error getting library records by criteria:', error);
            throw error;
        }
    },

    async searchAndGetByCriteria(payload: {
        guid?: string;
        user_guid?: string;
        book_name?: string;
    }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/librarys/search-and-get-by-criteria`, {
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
                throw new Error(result.data?.message || 'Failed to search and get library records');
            }
        } catch (error) {
            console.error('Error searching and getting library records:', error);
            throw error;
        }
    },

    async updateLastReadLibraryBookRecord(libraryGuid: string): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/librarys/update-last-read/${libraryGuid}`, {
                method: 'PUT',
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
                throw new Error(result.data?.message || 'Failed to update last read time');
            }
        } catch (error) {
            console.error('Error updating last read time:', error);
            throw error;
        }
    },
};


