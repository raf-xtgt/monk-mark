from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

"""
SQL Schema:
CREATE TABLE IF NOT EXISTS app_mm_notebook_llm_chat_hdr (
    guid UUID PRIMARY KEY,
    user_guid UUID,
    notebook_hdr_guid UUID,
    library_hdr_guid UUID,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    updated_date TIMESTAMPTZ DEFAULT NOW()
);
"""

class AppMmNotebookLlmChatHdrCreate(BaseModel):
    user_guid: UUID
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None

class AppMmNotebookLlmChatHdrUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None

class AppMmNotebookLlmChatHdrResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
