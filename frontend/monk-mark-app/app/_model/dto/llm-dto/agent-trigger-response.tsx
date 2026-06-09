export interface AgentTriggerResponse {
    session_id: string;
    responses: string[];
    storage_url: string | null;
    visual_metaphor_prompt: string | null;
}
