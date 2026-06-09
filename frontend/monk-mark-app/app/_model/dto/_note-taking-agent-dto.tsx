export interface NoteTakingAgentRequest {
  notebook_hdr_guid: string;
  notebook_content_guid: string;
  image_url: string;
  highlight_metadata: {
    highlights: Array<{
      x: number;
      y: number;
      width: number;
      height: number;
    }>;
  };
}

export interface NoteTakingAgentResponse {
  session_id: string;
  generated_note: string | null;
  responses: string[];
}
