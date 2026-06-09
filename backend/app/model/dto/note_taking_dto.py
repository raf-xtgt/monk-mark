from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class NoteTakingAgentRequest(BaseModel):
    """Request payload for triggering the note-taking agent."""
    notebook_hdr_guid: UUID
    notebook_content_guid: UUID
    image_url: str
    highlight_metadata: dict


class NoteTakingAgentResponse(BaseModel):
    """Response from the note-taking agent."""
    session_id: str
    generated_note: Optional[str] = None
    responses: List[str] = []
