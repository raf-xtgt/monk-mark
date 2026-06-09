from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AppMmUserCreate(BaseModel):
    email: str

class AppMmUserUpdate(BaseModel):
    email: Optional[str] = None

class AppMmUserResponse(BaseModel):
    guid: UUID
    email: str
    created_date: datetime

    class Config:
        from_attributes = True