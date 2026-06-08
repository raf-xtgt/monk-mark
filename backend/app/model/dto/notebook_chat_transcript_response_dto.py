from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from typing import List
from model.notebook.app_mm_notebook_llm_chat_transcript import (
    AppMmNotebookLlmChatTranscriptResponse
)

class NotebookChatTranscriptResponseDto(BaseModel):
    chat_hdr_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    chat_transcripts: List[AppMmNotebookLlmChatTranscriptResponse] = []
    
