

import { API_BASE_URL } from '../_constants/api-constants';

export const UserService = {
    async autoCreateDefaultUser(payload: { email: string }): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/users/create`, {
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
                throw new Error(result.data?.message || 'Failed to create user');
            }
        } catch (error) {
            console.error('Error creating user:', error);
            throw error;
        }
    },
};


