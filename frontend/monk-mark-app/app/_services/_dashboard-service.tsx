import { API_BASE_URL } from '../_constants/api-constants';
import { DashboardStats, DashboardNotebook, DashboardLegacyArt, DashboardLegacyArtByHdr } from '../_model/dto/_dashboard-dto';

export const DashboardService = {
  async getUserStats(userGuid: string): Promise<DashboardStats> {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/stats/${userGuid}`, {
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
        throw new Error(result.data?.message || 'Failed to get user stats');
      }
    } catch (error) {
      console.error('Error getting user stats:', error);
      throw error;
    }
  },

  async getUserNotebooks(userGuid: string): Promise<DashboardNotebook[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/notebooks/${userGuid}`, {
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
        throw new Error(result.data?.message || 'Failed to get user notebooks');
      }
    } catch (error) {
      console.error('Error getting user notebooks:', error);
      throw error;
    }
  },

  async getUserLegacyArts(userGuid: string): Promise<DashboardLegacyArt[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/legacy-arts/${userGuid}`, {
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
        throw new Error(result.data?.message || 'Failed to get user legacy arts');
      }
    } catch (error) {
      console.error('Error getting user legacy arts:', error);
      throw error;
    }
  },

  async getUserLegacyArtsByHdr(userGuid: string): Promise<DashboardLegacyArtByHdr[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/legacy-arts-by-hdr/${userGuid}`, {
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
        throw new Error(result.data?.message || 'Failed to get user legacy arts by hdr');
      }
    } catch (error) {
      console.error('Error getting user legacy arts by hdr:', error);
      throw error;
    }
  },

};
