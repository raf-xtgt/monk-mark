from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class LibraryHdrQueryCriteria(BaseModel):
    guid: Optional[UUID] = None
    user_guid: Optional[UUID] = None
    book_name: Optional[str] = None
