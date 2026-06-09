import { API_BASE_URL } from '../_constants/api-constants';
import { RewardHdr, MilestoneEvaluation, RewardSummary } from '../_model/dto/reward-output-dto';
export type { RewardHdr, MilestoneEvaluation, RewardSummary };

export const RewardHdrService = {
    async createRewardHdr(payload: {
        userGuid: string;
        libraryHdrGuid: string;
        notebookHdrGuid: string;
        imageUrl?: string;
        fileUploadGuid?: string;
        rewardMetadata?: any;
    }): Promise<RewardHdr> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    notebook_hdr_guid: payload.notebookHdrGuid,
                    image_url: payload.imageUrl,
                    file_upload_guid: payload.fileUploadGuid,
                    reward_metadata: payload.rewardMetadata,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardHdr;
            } else {
                throw new Error(result.data?.message || 'Failed to create reward header');
            }
        } catch (error) {
            console.error('Error creating reward header:', error);
            throw error;
        }
    },

    async getRewardHdrByGuid(rewardId: string): Promise<RewardHdr | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/get-by-guid/${rewardId}`, {
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
                return result.data as RewardHdr;
            }

            return null;
        } catch (error) {
            console.error('Error getting reward header:', error);
            throw error;
        }
    },

    async getAllRewardHdrs(): Promise<RewardHdr[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/get-all`, {
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
                return result.data as RewardHdr[];
            }

            return [];
        } catch (error) {
            console.error('Error getting all reward headers:', error);
            throw error;
        }
    },

    async getRewardHdrsByUser(userGuid: string): Promise<RewardHdr[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/get-by-user/${userGuid}`, {
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
                return result.data as RewardHdr[];
            }

            return [];
        } catch (error) {
            console.error('Error getting reward headers by user:', error);
            throw error;
        }
    },

    async getRewardHdrsByNotebook(notebookHdrGuid: string): Promise<RewardHdr[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/get-by-notebook/${notebookHdrGuid}`, {
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
                return result.data as RewardHdr[];
            }

            return [];
        } catch (error) {
            console.error('Error getting reward headers by notebook:', error);
            throw error;
        }
    },

    async updateRewardHdr(payload: {
        rewardId: string;
        userGuid?: string;
        libraryHdrGuid?: string;
        notebookHdrGuid?: string;
        imageUrl?: string;
        fileUploadGuid?: string;
        rewardMetadata?: any;
    }): Promise<RewardHdr> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/update/${payload.rewardId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    notebook_hdr_guid: payload.notebookHdrGuid,
                    image_url: payload.imageUrl,
                    file_upload_guid: payload.fileUploadGuid,
                    reward_metadata: payload.rewardMetadata,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardHdr;
            } else {
                throw new Error(result.data?.message || 'Failed to update reward header');
            }
        } catch (error) {
            console.error('Error updating reward header:', error);
            throw error;
        }
    },

    async deleteRewardHdr(rewardId: string): Promise<boolean> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/delete-by-guid/${rewardId}`, {
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
            console.error('Error deleting reward header:', error);
            throw error;
        }
    },

    async getRewardSummaryByLibrary(userGuid: string, libraryHdrGuid: string): Promise<RewardSummary> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/get-summary-by-library/${userGuid}/${libraryHdrGuid}`, {
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
                return result.data as RewardSummary;
            } else {
                throw new Error(result.data?.message || 'Failed to get reward summary');
            }
        } catch (error) {
            console.error('Error getting reward summary by library:', error);
            throw error;
        }
    },

    async evaluateRewardMilestone(payload: RewardSummary): Promise<RewardSummary> {
        try {
            const response = await fetch(`${API_BASE_URL}/reward-hdrs/evaluate-milestone`, {
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

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as RewardSummary;
            } else {
                throw new Error(result.data?.message || 'Failed to evaluate reward milestone');
            }
        } catch (error) {
            console.error('Error evaluating reward milestone:', error);
            throw error;
        }
    },
};
