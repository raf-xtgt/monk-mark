export interface GitlabAgentOutput {
    issue_result: string | null;
    issue_url: string | null;
    branch_result: string | null;
    mr_result: string | null;
    visual_motif_result: string | null;
}

export interface AgentTriggerResponse {
    session_id: string;
    responses: string[];
    storage_url: string | null;
    visual_metaphor_prompt: string | null;
    gitlab_output: GitlabAgentOutput | null;
}
