from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class AppMmNotebookContentCreate(BaseModel):
    user_guid: UUID
    notebook_hdr_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    content_text: Optional[str] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None
    sequence_no: Optional[int] = None

class AppMmNotebookContentUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    content_text: Optional[str] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None
    sequence_no: Optional[int] = None

class AppMmNotebookContentResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    notebook_hdr_guid: UUID
    library_hdr_guid: Optional[UUID] = None
    focus_session_guid: Optional[UUID] = None
    content_text: Optional[str] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None
    sequence_no: Optional[int] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
