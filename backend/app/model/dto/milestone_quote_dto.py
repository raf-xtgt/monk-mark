from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class MilestoneQuoteRequest(BaseModel):
    """Request payload for triggering the milestone quote agent."""
    library_hdr_guid: UUID
    reward_hdr_guid: Optional[UUID] = None


class MilestoneQuoteResponse(BaseModel):
    """Response from the milestone quote agent."""
    session_id: str
    quote: Optional[str] = None
    responses: List[str] = []
