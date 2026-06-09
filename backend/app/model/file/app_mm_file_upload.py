from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class AppMmFileUploadCreate(BaseModel):
    user_guid: UUID
    file_name: str
    mime_type: str
    metadata: Optional[Dict[str, Any]] = None
    storage_path: str
    bucket_name: str
    is_public: bool = False

class AppMmFileUploadUpdate(BaseModel):
    user_guid: Optional[UUID] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    storage_path: Optional[str] = None
    bucket_name: Optional[str] = None
    is_public: Optional[bool] = None

class AppMmFileUploadResponse(BaseModel):
    guid: UUID
    user_guid: UUID
    file_name: str
    mime_type: str
    metadata: Optional[Dict[str, Any]] = None
    storage_path: str
    bucket_name: str
    is_public: bool
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True
