from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional
from model.api_response import ApiResponse
from service.agents.tools.reading_context_tool import build_reading_context

router = APIRouter(prefix="/context", tags=["context"])


class ReadingContextRequest(BaseModel):
    user_guid: str
    library_hdr_guid: str
    notebook_hdr_guid: str
    llm_chat_hdr_guid: Optional[str] = None
    max_chars: Optional[int] = None


@router.post("/build-reading-context", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def post_build_reading_context(request: ReadingContextRequest):
    """Build a sanitized reading context string from book metadata, notebook content, and chat transcripts."""
    try:
        kwargs = {
            "user_guid": request.user_guid,
            "library_hdr_guid": request.library_hdr_guid,
            "notebook_hdr_guid": request.notebook_hdr_guid,
        }
        if request.llm_chat_hdr_guid:
            kwargs["llm_chat_hdr_guid"] = request.llm_chat_hdr_guid
        if request.max_chars is not None:
            kwargs["max_chars"] = request.max_chars

        result = build_reading_context(**kwargs)

        if result.get("status") == "success":
            return ApiResponse.success(result)
        return ApiResponse.error(result)
    except Exception as e:
        return ApiResponse.error({"message": str(e)})
