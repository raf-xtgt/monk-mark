export interface DashboardStats {
  user_guid: string;
  total_focused_hrs: number;
  total_notes: number;
}

export interface DashboardNotebook {
  notebook_hdr_guid: string;
  library_hdr_guid: string;
  notebook_name: string;
  total_notes: number;
  last_updated: string | null;
}

export interface DashboardLegacyArt {
  reward_hdr_guid: string;
  reward_line_guid: string;
  reward_line_image_url: string;
  tier_level: number | null;
  notebook_hdr_guid: string;
  library_hdr_guid: string;
  notebook_name: string;
}

export interface RewardLine {
  guid: string;
  user_guid: string;
  reward_hdr_guid: string;
  file_upload_guid: string | null;
  image_url: string | null;
  tier_level: number | null;
  art_prompt: string | null;
  created_date: string;
  updated_date: string;
}

export interface GitlabSyncLog {
  guid: string;
  user_guid: string | null;
  focus_session_guid: string | null;
  notebook_hdr_guid: string | null;
  library_hdr_guid: string | null;
  llm_chat_hdr_guid: string | null;
  reward_line_guid: string | null;
  branch_name: string | null;
  issue_url: string | null;
  merge_request_url: string | null;
  file_url: string | null;
  sync_status: string | null;
  created_date: string;
  updated_date: string;
}

export interface RewardLineWithSyncLog {
  reward_line: RewardLine;
  gitlab_sync_log: GitlabSyncLog | null;
}

export interface DashboardLegacyArtByHdr {
  reward_hdr_guid: string;
  reward_hdr_tier_level: number | null;
  reward_hdr_library_guid: string;
  reward_hdr_notebook_guid: string;
  reward_lines: RewardLineWithSyncLog[];
}
