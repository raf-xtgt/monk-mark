from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class NotebookFileContentDto(BaseModel):
    notebook_content_file_guid: UUID
    image_url: Optional[str] = None


class NotebookChatTranscriptDto(BaseModel):
    chat_transcript_guid: UUID
    sender: str
    msg_content: str


class GitlabAgentContextDto(BaseModel):
    user_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    book_name: Optional[str] = None
    book_desc: Optional[str] = None
    notebook_hdr_guid: Optional[UUID] = None
    notebook_name: Optional[str] = None
    notebook_content_text: List[str] = []
    notebook_content_file: List[NotebookFileContentDto] = []
    llm_chat_hdr_guid: Optional[UUID] = None
    llm_chat_transcript: List[NotebookChatTranscriptDto] = []


class GitlabContextRequest(BaseModel):
    """Request payload for retrieving gitlab agent context."""
    user_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    llm_chat_hdr_guid: Optional[UUID] = None


class GitlabNoteDto(BaseModel):
    temp_image_file: Optional[str] = None
    note_content: str
    image_ref: str
