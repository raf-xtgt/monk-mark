from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AppMmNotebookLlmChatTranscriptCreate(BaseModel):
    user_guid: UUID
    llm_chat_hdr_guid: UUID
    msg_content: str
    sender: str
    focus_session_guid: Optional[UUID] = None

class AppMmNotebookLlmChatTranscriptUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    llm_chat_hdr_guid: Optional[UUID] = None
    msg_content: Optional[str] = None
    sender: Optional[str] = None
    focus_session_guid: Optional[UUID] = None

class AppMmNotebookLlmChatTranscriptResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    llm_chat_hdr_guid: UUID
    msg_content: str
    sender: str
    focus_session_guid: Optional[UUID] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
