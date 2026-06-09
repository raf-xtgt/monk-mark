from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class AppMmRewardLineCreate(BaseModel):
    user_guid: UUID
    reward_hdr_guid: UUID
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    tier_level: Optional[int] = None
    art_prompt: Optional[str] = None


class AppMmRewardLineUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    reward_hdr_guid: Optional[UUID] = None
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    tier_level: Optional[int] = None
    art_prompt: Optional[str] = None


class AppMmRewardLineResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    reward_hdr_guid: UUID
    file_upload_guid: Optional[UUID] = None
    image_url: Optional[str] = None
    tier_level: Optional[int] = None
    art_prompt: Optional[str] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
