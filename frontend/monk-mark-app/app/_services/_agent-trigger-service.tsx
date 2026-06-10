import { API_BASE_URL } from '../_constants/api-constants';
import { AgentTriggerResponse } from '../_model/dto/llm-dto/agent-trigger-response';
import { MilestoneQuoteRequest, MilestoneQuoteResponse } from '../_model/dto/llm-dto/_milestone_quote_agent_dto';
import { GitlabAgentTriggerRequest } from '../_model/dto/llm-dto/_gitlab_agent_dto';

export interface AgentTriggerRequest {
    userGuid: string;
    libraryHdrGuid: string;
    notebookHdrGuid: string;
    llmChatHdrGuid?: string;
    eventType: string;
    message?: string;
}

export interface ArtGenerationRequest {
    userGuid: string;
    visualMotif?: string;
}

export interface ArtEvolutionRequest {
    userGuid: string;
    libraryHdrGuid: string;
    visualMotif?: string;
}

export type { AgentTriggerResponse, GitlabAgentTriggerRequest };

export const AgentTriggerService = {
    async triggerAgent(payload: AgentTriggerRequest): Promise<AgentTriggerResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/agent/trigger`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    notebook_hdr_guid: payload.notebookHdrGuid,
                    llm_chat_hdr_guid: payload.llmChatHdrGuid,
                    event_type: payload.eventType,
                    message: payload.message,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as AgentTriggerResponse;
            } else {
                throw new Error(result.data?.message || 'Failed to trigger agent');
            }
        } catch (error) {
            console.error('Error triggering agent:', error);
            throw error;
        }
    },

    async triggerMilestoneQuote(payload: MilestoneQuoteRequest): Promise<MilestoneQuoteResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/agent/trigger-milestone-quote`, {
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
                return result.data as MilestoneQuoteResponse;
            } else {
                throw new Error(result.data?.message || 'Failed to trigger milestone quote agent');
            }
        } catch (error) {
            console.error('Error triggering milestone quote agent:', error);
            throw error;
        }
    },

    async triggerGitlabAgent(payload: GitlabAgentTriggerRequest): Promise<AgentTriggerResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/agent/trigger-gitlab`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    focus_session_guid: payload.focusSessionGuid,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as AgentTriggerResponse;
            } else {
                throw new Error(result.data?.message || 'Failed to trigger gitlab agent');
            }
        } catch (error) {
            console.error('Error triggering gitlab agent:', error);
            throw error;
        }
    },

    async triggerArtAgent(payload: ArtGenerationRequest): Promise<AgentTriggerResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/agent/trigger-art`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    visual_motif: payload.visualMotif,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as AgentTriggerResponse;
            } else {
                throw new Error(result.data?.message || 'Failed to trigger art agent');
            }
        } catch (error) {
            console.error('Error triggering art agent:', error);
            throw error;
        }
    },

    async triggerArtEvolutionAgent(payload: ArtEvolutionRequest): Promise<AgentTriggerResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/agent/trigger-art-evolution`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_guid: payload.userGuid,
                    library_hdr_guid: payload.libraryHdrGuid,
                    visual_motif: payload.visualMotif,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'OK_RESPONSE' && result.data) {
                return result.data as AgentTriggerResponse;
            } else {
                throw new Error(result.data?.message || 'Failed to trigger art evolution agent');
            }
        } catch (error) {
            console.error('Error triggering art evolution agent:', error);
            throw error;
        }
    },
};
