export interface RewardHdr {
    guid: string;
    user_guid: string;
    library_hdr_guid: string;
    notebook_hdr_guid: string;
    image_url: string | null;
    file_upload_guid: string | null;
    reward_metadata: any | null;
    created_date: string;
    updated_date: string;
}

export interface MilestoneEvaluation {
    current_tier: number;
    next_tier: number;
    hour_threshold: number;
    note_threshold: number;
    hour_completion_percentage: number;
    note_completion_percentage: number;
    note_completion_ratio: string;
    is_hour_fulfilled: boolean;
    is_note_fulfilled: boolean;
    agent_to_trigger: 'ART_GEN' | 'ART_EVOLUTION' | 'NO_AGENT';
    remarks?: string | null;
    remaining_hours?: number | null;
    remaining_notes?: number | null;
}

export interface RewardSummary {
    user_guid: string;
    library_hdr_guid: string | null;
    reward_list: RewardHdr[];
    total_focused_hrs: number;
    total_notes: number;
    milestone_evaluation?: MilestoneEvaluation | null;
}
