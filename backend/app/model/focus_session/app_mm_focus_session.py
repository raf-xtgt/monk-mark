from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class AppMmFocusSessionCreate(BaseModel):
    user_guid: UUID
    library_hdr_guid: UUID
    time_hrs: Optional[Decimal] = None
    time_seconds: Optional[int] = None

class AppMmFocusSessionUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    library_hdr_guid: Optional[UUID] = None
    time_hrs: Optional[Decimal] = None
    time_seconds: Optional[int] = None

class AppMmFocusSessionResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    library_hdr_guid: UUID
    time_hrs: Optional[Decimal] = None
    time_seconds: Optional[int] = None
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
