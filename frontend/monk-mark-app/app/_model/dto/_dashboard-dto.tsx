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

export interface DashboardLegacyArtByHdr {
  reward_hdr_guid: string;
  reward_hdr_tier_level: number | null;
  reward_hdr_library_guid: string;
  reward_hdr_notebook_guid: string;
  reward_lines: RewardLine[];
}
