from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FocusSessionQueryCriteria(BaseModel):
    guid: Optional[UUID]
    user_guid: Optional[UUID]
    library_hdr_guid: Optional[UUID]
    

