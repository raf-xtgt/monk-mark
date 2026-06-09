# backend/app/service/agents/tools/agent_tools.py
# Source: adk-local-docs/docs/tools-custom/function-tools.md

import logging
from uuid import UUID

from service.notebook.app_mm_notebook_llm_chat_transcript_service import NotebookLlmChatTranscriptService
from service.file.app_mm_file_upload_service import AppMmFileUploadService

from model.notebook.app_mm_notebook_llm_chat_transcript import AppMmNotebookLlmChatTranscriptCreate
from model.file.app_mm_file_upload import AppMmFileUploadCreate

logger = logging.getLogger(__name__)


def save_chat_transcript(user_guid: str, llm_chat_hdr_guid: str, msg_content: str, sender: str, focus_session_guid: str = None) -> dict:
    """Persists a chat message to the transcript table.

    Args:
        user_guid: The UUID of the user.
        llm_chat_hdr_guid: The UUID of the LLM chat header.
        msg_content: The message text content.
        sender: The sender identifier ('user' or 'assistant').
        focus_session_guid: Optional UUID of the focus session.

    Returns:
        dict with 'status' and either 'data' (created record) or error details.
    """
    try:
        data = AppMmNotebookLlmChatTranscriptCreate(
            user_guid=UUID(user_guid),
            llm_chat_hdr_guid=UUID(llm_chat_hdr_guid),
            msg_content=msg_content,
            sender=sender,
            focus_session_guid=UUID(focus_session_guid) if focus_session_guid else None,
        )
        result = NotebookLlmChatTranscriptService.create_transcript(data)
        return {"status": "success", "data": result.model_dump(mode="json")}
    except Exception as e:
        logger.error(f"save_chat_transcript error: {e}", exc_info=True)
        return {"status": "error", "error_type": type(e).__name__, "message": str(e)}


def upload_file_to_storage(user_guid: str, file_name: str, mime_type: str, storage_path: str, bucket_name: str) -> dict:
    """Uploads a file record to Supabase storage tracking.

    Args:
        user_guid: The UUID of the user.
        file_name: Name of the file.
        mime_type: MIME type of the file (e.g., 'image/png').
        storage_path: Path in Supabase storage.
        bucket_name: Supabase storage bucket name.

    Returns:
        dict with 'status' and either 'data' (created file record) or error details.
    """
    try:
        data = AppMmFileUploadCreate(
            user_guid=UUID(user_guid),
            file_name=file_name,
            mime_type=mime_type,
            storage_path=storage_path,
            bucket_name=bucket_name,
        )
        result = AppMmFileUploadService.create_file_upload(data)
        return {"status": "success", "data": result.model_dump(mode="json")}
    except Exception as e:
        logger.error(f"upload_file_to_storage error: {e}", exc_info=True)
        return {"status": "error", "error_type": type(e).__name__, "message": str(e)}
