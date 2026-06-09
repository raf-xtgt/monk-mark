from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class AppMmNotebookContentFileLinkCreate(BaseModel):
    user_guid: UUID
    notebook_hdr_guid: UUID
    notebook_content_guid: Optional[UUID] = None
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None

class AppMmNotebookContentFileLinkUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    notebook_content_guid: Optional[UUID] = None
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None

class AppMmNotebookContentFileLinkResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    notebook_hdr_guid: UUID
    notebook_content_guid: Optional[UUID] = None
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    highlight_metadata: Optional[Dict[str, Any]] = None
    sequence_no: int
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
