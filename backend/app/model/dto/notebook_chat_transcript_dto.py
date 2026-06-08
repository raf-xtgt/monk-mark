from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class NotebookChatTranscriptDto(BaseModel):
    notebook_hdr_guid: UUID
    user_guid: UUID
    library_hdr_guid: Optional[UUID] = None
