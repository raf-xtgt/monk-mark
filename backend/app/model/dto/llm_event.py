from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from uuid import UUID


class LLMEvent(BaseModel):
    event_guid: UUID
    event_type: str
    event_context: Optional[List[Dict[str, Any]]] = None
