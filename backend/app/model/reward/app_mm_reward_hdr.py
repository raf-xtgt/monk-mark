from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


class AppMmRewardHdrCreate(BaseModel):
    user_guid: UUID
    library_hdr_guid: UUID
    notebook_hdr_guid: UUID
    image_url: Optional[str] = None
    file_upload_guid: Optional[UUID] = None
    tier_level: Optional[int] = None
    trigger_session_guid: Optional[UUID] = None
    reward_metadata: Optional[Any] = None


class AppMmRewardHdrUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    notebook_hdr_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    file_upload_guid: Optional[UUID] = None
    tier_level: Optional[int] = None
    trigger_session_guid: Optional[UUID] = None
    reward_metadata: Optional[Any] = None


class AppMmRewardHdrResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    library_hdr_guid: UUID
    notebook_hdr_guid: UUID
    image_url: Optional[str] = None
    file_upload_guid: Optional[UUID] = None
    tier_level: Optional[int] = None
    trigger_session_guid: Optional[UUID] = None
    reward_metadata: Optional[Any] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
