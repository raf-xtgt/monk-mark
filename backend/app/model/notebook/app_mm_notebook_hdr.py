from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AppMmNotebookHdrCreate(BaseModel):
    user_guid: UUID
    library_hdr_guid: UUID
    running_no: str
    name: str

class AppMmNotebookHdrUpdate(BaseModel):
    running_no: Optional[str] = None
    name: Optional[str] = None
    updated_date: Optional[datetime] = None

class AppMmNotebookHdrResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    library_hdr_guid: UUID
    running_no: str
    name: str
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
