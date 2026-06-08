from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AppMmLibraryHdrCreate(BaseModel):
    user_guid: UUID
    book_name: str
    book_desc: Optional[str] = None
    file_guid: Optional[UUID] = None

class AppMmLibraryHdrUpdate(BaseModel):
    book_name: Optional[str] = None
    book_desc: Optional[str] = None
    last_read: Optional[datetime] = None
    file_guid: Optional[UUID] = None

class AppMmLibraryHdrResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    book_name: str
    book_desc: Optional[str]
    file_guid: Optional[UUID]
    created_date: datetime
    last_read: datetime

    class Config:
        from_attributes = True

class AppMmLibraryHdrWithFileResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    book_name: str
    book_desc: Optional[str]
    file_guid: Optional[UUID]
    created_date: datetime
    last_read: datetime
    storage_path: Optional[str] = None
    session_count: Optional[int] = 0
    time_focused_hrs: Optional[float] = 0.0
    time_focused_minutes: Optional[int] = 0
    focus_time: Optional[str] = "0h 0min"

    class Config:
        from_attributes = True
