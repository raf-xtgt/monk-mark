export interface MilestoneQuoteRequest {
  library_hdr_guid: string;
  reward_hdr_guid?: string;
}

export interface MilestoneQuoteResponse {
  session_id: string;
  quote: string | null;
  responses: string[];
}
