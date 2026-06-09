import { API_BASE_URL } from '../_constants/api-constants';

export interface RewardLine {
    guid: string;
    user_guid: string;
    reward_hdr_guid: string;
    file_upload_guid?: string | null;
    image_url?: string | null;
    tier_level?: number | null;
    created_date: string;
    updated_date: string;
}

export const RewardLineService = {
    async createRewardLine(payload: {
        userGuid: string;
        rewardHdrGuid: string;
        fileUploadGuid?: string;
        imageUrl?: string;
        tierLevel?: number;
    }): Promise<RewardLine> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    reward_hdr_guid: payload.rewardHdrGuid,
                    file_upload_guid: payload.fileUploadGuid,
                    image_url: payload.imageUrl,
                    tier_level: payload.tierLevel,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine;
            } else {
                throw new Error(result.data?.message || 'Failed to create reward line');
            }
        } catch (error) {
            console.error('Error creating reward line:', error);
            throw error;
        }
    },

    async getRewardLineByGuid(rewardLineId: string): Promise<RewardLine | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/get-by-guid/${rewardLineId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine;
            }

            return null;
        } catch (error) {
            console.error('Error getting reward line:', error);
            throw error;
        }
    },

    async getAllRewardLines(): Promise<RewardLine[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/get-all`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine[];
            }

            return [];
        } catch (error) {
            console.error('Error getting all reward lines:', error);
            throw error;
        }
    },

    async getRewardLinesByUser(userGuid: string): Promise<RewardLine[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/get-by-user/${userGuid}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine[];
            }

            return [];
        } catch (error) {
            console.error('Error getting reward lines by user:', error);
            throw error;
        }
    },

    async getRewardLinesByRewardHdr(rewardHdrGuid: string): Promise<RewardLine[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/get-by-reward-hdr/${rewardHdrGuid}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine[];
            }

            return [];
        } catch (error) {
            console.error('Error getting reward lines by reward header:', error);
            throw error;
        }
    },

    async updateRewardLine(payload: {
        rewardLineId: string;
        userGuid?: string;
        rewardHdrGuid?: string;
        fileUploadGuid?: string;
        imageUrl?: string;
        tierLevel?: number;
    }): Promise<RewardLine> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/update/${payload.rewardLineId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    reward_hdr_guid: payload.rewardHdrGuid,
                    file_upload_guid: payload.fileUploadGuid,
                    image_url: payload.imageUrl,
                    tier_level: payload.tierLevel,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardLine;
            } else {
                throw new Error(result.data?.message || 'Failed to update reward line');
            }
        } catch (error) {
            console.error('Error updating reward line:', error);
            throw error;
        }
    },

    async deleteRewardLine(rewardLineId: string): Promise<boolean> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-lines/delete-by-guid/${rewardLineId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            return result.status === 'OK_RESPONSE';
        } catch (error) {
            console.error('Error deleting reward line:', error);
            throw error;
        }
    },
};
