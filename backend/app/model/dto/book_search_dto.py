from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BookSearchRequestDto(BaseModel):
    book_name: str
    user_guid: UUID

class BookSearchResponseDto(BaseModel):
    guid: UUID
    book_name: str
    author: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    file_guid: Optional[UUID] = None
